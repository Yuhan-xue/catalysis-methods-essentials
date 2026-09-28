# lab05_potential.py --- turning points and period from a potential U(x)
# U(x) = 0.5*w0^2*x^2 + beta*x^4, m = 1. Depends on numpy, matplotlib.
import numpy as np
import matplotlib.pyplot as plt

m = 1.0
w0 = 1.0
beta = 0.1


def U(x):
    return 0.5 * m * w0 ** 2 * x ** 2 + beta * x ** 4


def force(x):
    return -(m * w0 ** 2 * x + 4.0 * beta * x ** 3)


def turning_point(E):
    # solve U(x) = E for x > 0 by bisection on a bracket found by scanning
    grid = np.linspace(1.0e-9, 5.0, 200001)
    val = U(grid) - E
    idx = np.where(val > 0.0)[0]
    if idx.size == 0:
        raise ValueError("energy above every sampled turning point")
    lo, hi = grid[idx[0] - 1], grid[idx[0]]
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if U(mid) - E > 0.0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def trapz(y, x):
    # 手写梯形积分，避免依赖 numpy 2.0 才有的 np.trapezoid
    return np.sum(0.5 * (y[1:] + y[:-1]) * np.diff(x))


def period_quadrature(E, n=200001):
    # x = xm*sin(phi) removes the inverse-square-root singularity at the turning point
    xm = turning_point(E)
    phi = np.linspace(0.0, 0.5 * np.pi, n)
    x = xm * np.sin(phi)
    v = np.sqrt(np.maximum(2.0 * (E - U(x)) / m, 0.0))
    integrand = np.where(v > 1.0e-300, xm * np.cos(phi) / np.maximum(v, 1.0e-300), 0.0)
    return 4.0 * trapz(integrand, phi)


def period_rk4(E, dt=1.0e-4, tmax=60.0):
    x, v = turning_point(E), 0.0
    t, tcross = 0.0, []
    while t < tmax:
        k1x, k1v = v, force(x) / m
        k2x, k2v = v + 0.5 * dt * k1v, force(x + 0.5 * dt * k1x) / m
        k3x, k3v = v + 0.5 * dt * k2v, force(x + 0.5 * dt * k2x) / m
        k4x, k4v = v + dt * k3v, force(x + dt * k3x) / m
        x_new = x + dt / 6.0 * (k1x + 2.0 * k2x + 2.0 * k3x + k4x)
        v = v + dt / 6.0 * (k1v + 2.0 * k2v + 2.0 * k3v + k4v)
        t += dt
        if x < 0.0 <= x_new:                       # upward crossing of x = 0
            tcross.append(t - dt * x_new / (x_new - x))
        x = x_new
    if len(tcross) < 3:
        return np.nan
    return tcross[-1] - tcross[-2]


print("small-oscillation limit: T -> 2*pi/w0 = %.6f" % (2.0 * np.pi / w0))
print("")
print("%8s %10s %14s %12s %12s" % ("E", "x_max", "T_quadrature", "T_RK4", "rel.diff"))
for E in (0.01, 0.1, 0.5, 2.0, 10.0):
    xm = turning_point(E)
    Tq = period_quadrature(E)
    Tr = period_rk4(E, dt=2.0e-5 if E > 5.0 else 1.0e-4)
    print("%8.3f %10.5f %14.6f %12.6f %12.2e" % (E, xm, Tq, Tr, abs(Tq - Tr) / Tq))

fig, ax = plt.subplots(1, 2, figsize=(11.0, 4.2))
xx = np.linspace(-2.2, 2.2, 600)
ax[0].plot(xx, U(xx), "k-", lw=1.6, label="$U(x)$")
for E, col in ((0.1, "b"), (0.5, "r"), (2.0, "g")):
    xm = turning_point(E)
    ax[0].axhline(E, color=col, ls="--", lw=0.9)
    ax[0].plot([-xm, xm], [E, E], color=col, marker="o", ls="none", ms=4)
ax[0].set_xlim(-2.2, 2.2)
ax[0].set_ylim(0.0, 3.2)
ax[0].set_xlabel("x")
ax[0].set_ylabel("U(x)")
ax[0].set_title("turning points at U = E")
ax[0].legend()

Es = np.linspace(0.001, 20.0, 60)
Ts = np.array([period_quadrature(E, n=20001) for E in Es])
ax[1].plot(Es, Ts, "k-")
ax[1].axhline(2.0 * np.pi / w0, color="r", ls="--", lw=0.9, label="$2\\pi/\\omega_0$")
ax[1].set_xlabel("energy E")
ax[1].set_ylabel("period T")
ax[1].set_title("period shortens as the spring stiffens")
ax[1].legend()
fig.tight_layout()
plt.show()
