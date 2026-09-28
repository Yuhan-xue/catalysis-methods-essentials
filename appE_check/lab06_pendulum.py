# lab06_pendulum.py --- small angle vs exact vs damped vs driven, resonance width
# Depends on numpy, matplotlib.
import numpy as np
import matplotlib.pyplot as plt

g, L = 9.80665, 1.0
w0 = np.sqrt(g / L)


def ellip_K(k):
    # complete elliptic integral of the first kind by the arithmetic-geometric mean
    a, b = 1.0, np.sqrt(1.0 - k ** 2)
    for _ in range(40):
        a, b = 0.5 * (a + b), np.sqrt(a * b)
    return 0.5 * np.pi / a


def period_exact(theta0):
    return 4.0 * np.sqrt(L / g) * ellip_K(np.sin(0.5 * theta0))


def integrate(theta0, tmax, gamma=0.0, drive=0.0, omega_d=0.0, dt=1.0e-4,
              linear=False, x0=None, v0=0.0):
    th, om = (theta0, 0.0) if x0 is None else (x0, v0)
    ts, ths = [0.0], [th]

    def rhs(th, om, t):
        acc = -(g / L) * (th if linear else np.sin(th)) - 2.0 * gamma * om
        acc += drive * np.cos(omega_d * t)
        return om, acc

    t = 0.0
    peaked = []
    for _ in range(int(tmax / dt)):
        k1 = rhs(th, om, t)
        k2 = rhs(th + 0.5 * dt * k1[0], om + 0.5 * dt * k1[1], t + 0.5 * dt)
        k3 = rhs(th + 0.5 * dt * k2[0], om + 0.5 * dt * k2[1], t + 0.5 * dt)
        k4 = rhs(th + dt * k3[0], om + dt * k3[1], t + dt)
        th_new = th + dt / 6.0 * (k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0])
        om = om + dt / 6.0 * (k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1])
        t += dt
        if th < 0.0 <= th_new:                      # upward crossing of theta = 0
            peaked.append(t - dt * th_new / (th_new - th))
        th = th_new
        ts.append(t)
        ths.append(th)
    return np.array(ts), np.array(ths), peaked


print("omega0 = %.6f rad/s, small-angle period = %.6f s" % (w0, 2.0 * np.pi / w0))
print("")
print("%10s %14s %14s %12s" % ("theta0/deg", "T_exact/s", "T_RK4/s", "rel.diff"))
for deg in (5.0, 30.0, 90.0, 150.0, 170.0):
    th0 = np.deg2rad(deg)
    Te = period_exact(th0)
    ts, ths, peaked = integrate(th0, 4.0 * Te, dt=2.0e-4)
    Tr = peaked[-1] - peaked[-2]
    print("%10.1f %14.6f %14.6f %12.2e" % (deg, Te, Tr, abs(Te - Tr) / Te))

# --- damped ring-down: measure Q from the logarithmic decrement ---
gamma = 0.05
ts, ths, _ = integrate(np.deg2rad(10.0), 100.0, gamma=gamma, dt=2.0e-4)
peaks = [i for i in range(1, len(ths) - 1) if ths[i] > ths[i - 1] and ths[i] >= ths[i + 1]]
n1, n2 = peaks[0], peaks[3]
delta = np.log(ths[n1] / ths[n2]) / 3.0
print("")
print("damped: gamma = %.3f, Q_theory = %.4f, Q_from_decrement = %.4f"
      % (gamma, w0 / (2.0 * gamma), np.pi / delta))

# --- resonance curve of the driven linear oscillator ---
print("")
print("%8s %10s %12s %12s %12s" % ("gamma", "Q", "dw_theory", "dw_measured", "rel.diff"))
omega = np.linspace(0.5 * w0, 1.5 * w0, 400001)
for gamma in (0.05, 0.1, 0.25):
    f0 = 0.1
    A = f0 / np.sqrt((w0 ** 2 - omega ** 2) ** 2 + (2.0 * gamma * omega) ** 2)
    half = A.max() / np.sqrt(2.0)
    above = np.where(A >= half)[0]
    dw = omega[above[-1]] - omega[above[0]]
    print("%8.3f %10.3f %12.5f %12.5f %12.2e"
          % (gamma, w0 / (2.0 * gamma), 2.0 * gamma, dw, abs(2.0 * gamma - dw) / (2.0 * gamma)))

fig, ax = plt.subplots(1, 3, figsize=(13.0, 3.9))
for deg, col in ((5.0, "b"), (30.0, "g"), (90.0, "r"), (170.0, "k")):
    th0 = np.deg2rad(deg)
    ts, ths, _ = integrate(th0, 3.0 * period_exact(th0), dt=2.0e-4)
    ax[0].plot(ts, np.rad2deg(ths) / deg, col, lw=0.9, label="%g deg" % deg)
ax[0].set_xlabel("t (s)")
ax[0].set_ylabel("theta / theta0")
ax[0].set_title("large amplitude is not harmonic")
ax[0].legend(fontsize=8)

ts, ths, _ = integrate(np.deg2rad(10.0), 60.0, gamma=0.05, dt=2.0e-4)
ax[1].plot(ts, np.rad2deg(ths), "k-", lw=0.7)
ax[1].plot(ts, np.rad2deg(np.deg2rad(10.0) * np.exp(-0.05 * ts)), "r--", lw=0.9, label="envelope")
ax[1].plot(ts, -np.rad2deg(np.deg2rad(10.0) * np.exp(-0.05 * ts)), "r--", lw=0.9)
ax[1].set_xlabel("t (s)")
ax[1].set_ylabel("theta (deg)")
ax[1].set_title("damped ring-down")
ax[1].legend(fontsize=8)

for gamma, col in ((0.05, "b"), (0.1, "g"), (0.25, "r")):
    f0 = 0.1
    A = f0 / np.sqrt((w0 ** 2 - omega ** 2) ** 2 + (2.0 * gamma * omega) ** 2)
    ax[2].plot(omega / w0, A, col, lw=1.1, label="gamma = %.2f" % gamma)
    ax[2].plot([1.0], [f0 / (2.0 * gamma * w0)], col, "o", ms=4)
ax[2].set_xlabel("omega / omega0")
ax[2].set_ylabel("steady amplitude")
ax[2].set_title("resonance curves")
ax[2].legend(fontsize=8)
fig.tight_layout()
plt.show()
