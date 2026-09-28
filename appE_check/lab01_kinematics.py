# lab01_kinematics.py --- numerical differentiation and integration
# d/dt and integral: from a(t) get v(t) and x(t). Depends on numpy, matplotlib.
import numpy as np
import matplotlib.pyplot as plt


def a_exact(t):
    return 2.0 - 0.5 * t + 0.3 * np.sin(t)          # m/s^2, given acceleration


def v_exact(t):
    return 2.0 * t - 0.25 * t ** 2 - 0.3 * np.cos(t) + 0.3   # m/s, v(0) = 0


def x_exact(t):
    return t ** 2 - t ** 3 / 12.0 - 0.3 * np.sin(t) + 0.3 * t  # m, x(0) = 0


T, N = 10.0, 2000
t = np.linspace(0.0, T, N + 1)
dt = t[1] - t[0]
a = a_exact(t)

v = np.zeros_like(t)                  # trapezoid rule
for i in range(N):
    v[i + 1] = v[i] + 0.5 * (a[i] + a[i + 1]) * dt

v_rect = np.zeros_like(t)             # left rectangle rule
for i in range(N):
    v_rect[i + 1] = v_rect[i] + a[i] * dt

x = np.zeros_like(t)                  # trapezoid rule again
for i in range(N):
    x[i + 1] = x[i] + 0.5 * (v[i] + v[i + 1]) * dt

x_euler = np.zeros_like(t)            # explicit Euler chain
for i in range(N):
    x_euler[i + 1] = x_euler[i] + v_rect[i] * dt

print("dt = %.5f s, steps = %d" % (dt, N))
print("t = %5.2f s   v_exact = %9.5f   v_trap = %9.5f   v_rect = %9.5f"
      % (T, v_exact(T), v[-1], v_rect[-1]))
print("t = %5.2f s   x_exact = %9.5f   x_trap = %9.5f   x_euler = %9.5f"
      % (T, x_exact(T), x[-1], x_euler[-1]))

print("")
print("central-difference errors on a refined grid")
for M in (100, 200, 400, 800, 1600):
    tt = np.linspace(0.0, T, M + 1)
    h = tt[1] - tt[0]
    xx = x_exact(tt)
    vv = (xx[2:] - xx[:-2]) / (2.0 * h)
    aa = (xx[2:] - 2.0 * xx[1:-1] + xx[:-2]) / h ** 2
    ev = np.max(np.abs(vv - v_exact(tt[1:-1])))
    ea = np.max(np.abs(aa - a_exact(tt[1:-1])))
    print("  M = %5d   h = %.5f   max|dv| = %.3e   max|da| = %.3e" % (M, h, ev, ea))

fig, ax = plt.subplots(1, 3, figsize=(13.0, 3.8))
ax[0].plot(t, a, color="tab:red")
ax[0].set_xlabel("t (s)")
ax[0].set_ylabel("a (m/s$^2$)")
ax[0].set_title("given a(t)")

ax[1].plot(t, v_exact(t), "k-", lw=2.0, label="analytic")
ax[1].plot(t, v, "r--", label="trapezoid")
ax[1].plot(t, v_rect, "b:", label="rectangle")
ax[1].set_xlabel("t (s)")
ax[1].set_ylabel("v (m/s)")
ax[1].set_title("integrate once")
ax[1].legend()

ax[2].plot(t, x_exact(t), "k-", lw=2.0, label="analytic")
ax[2].plot(t, x, "r--", label="trapezoid")
ax[2].plot(t, x_euler, "b:", label="explicit Euler")
ax[2].set_xlabel("t (s)")
ax[2].set_ylabel("x (m)")
ax[2].set_title("integrate twice")
ax[2].legend()

fig.tight_layout()
plt.show()
