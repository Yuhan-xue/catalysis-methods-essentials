# lab09_euler_top.py --- torque-free rigid body, Euler equations, intermediate axis
# I1 < I2 < I3, so rotation about axis 2 is unstable. Depends on numpy, matplotlib.
import numpy as np
import matplotlib.pyplot as plt

I = np.array([1.0, 2.0, 3.0])


def rhs(w):
    w1, w2, w3 = w
    return np.array([(I[1] - I[2]) * w2 * w3 / I[0],
                     (I[2] - I[0]) * w3 * w1 / I[1],
                     (I[0] - I[1]) * w1 * w2 / I[2]])


def integrate(w0, tmax=40.0, dt=1.0e-3):
    w = np.array(w0, dtype=float)
    n = int(tmax / dt)
    ts = np.zeros(n + 1)
    ws = np.zeros((n + 1, 3))
    ws[0] = w
    L2_0 = np.dot(I * w, I * w)
    T_0 = 0.5 * np.dot(w, I * w)
    dL2 = dT = 0.0
    t_flip = np.inf
    flips = 0
    for i in range(n):
        k1 = rhs(w)
        k2 = rhs(w + 0.5 * dt * k1)
        k3 = rhs(w + 0.5 * dt * k2)
        k4 = rhs(w + dt * k3)
        w = w + dt / 6.0 * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        ts[i + 1] = (i + 1) * dt
        ws[i + 1] = w
        dL2 = max(dL2, abs(np.dot(I * w, I * w) - L2_0) / L2_0)
        dT = max(dT, abs(0.5 * np.dot(w, I * w) - T_0) / T_0)
        if ws[i, 1] * w[1] < 0.0:
            flips += 1
            if t_flip == np.inf:
                t_flip = (i + 1) * dt
    return ts, ws, dL2, dT, t_flip, flips


lam = np.sqrt((I[2] - I[1]) * (I[1] - I[0]) / (I[0] * I[2]))
print("principal moments I = (%.1f, %.1f, %.1f); axis 2 is the middle axis" % tuple(I))
print("linear theory for a perturbation on axis 2: growth rate lambda = %.4f" % lam)
print("")
print("%-32s %10s %10s %12s %-22s" % ("initial spin", "dL2/L2", "dT/T",
                                       "growth", "omega2 sign flip"))
cases = [("about axis 1 (smallest I)", (1.0, 1.0e-3, 0.0), (1, 2), False),
         ("about axis 2 (middle I)", (1.0e-3, 1.0, 0.0), (0, 2), True),
         ("about axis 3 (largest I)", (0.0, 1.0e-3, 1.0), (0, 1), False)]
results = {}
for name, w0, pert, watch_flip in cases:
    ts, ws, dL2, dT, t_flip, flips = integrate(w0)
    results[name] = (ts, ws)
    growth = np.abs(ws[:, pert]).max() / 1.0e-3
    if not watch_flip:
        note = "not meaningful here"
    elif flips == 0:
        note = "no"
    else:
        note = "yes, %d time at t = %.1f" % (flips, t_flip)
    print("%-32s %10.2e %10.2e %12.3e %-22s" % (name, dL2, dT, growth, note))

ts, ws = results["about axis 2 (middle I)"]
ts_mid, ws_mid, _, _, t_flip_mid, _ = integrate((1.0e-3, 1.0, 0.0))
w1 = np.abs(ws_mid[:, 0])
mask = (w1 > 2.0e-3) & (w1 < 0.3) & (ts_mid < t_flip_mid)   # first growth phase only
fitted = np.polyfit(ts_mid[mask], np.log(w1[mask]), 1)[0]
print("")
print("perturbation on axis 2 grows by a factor %.0f before the flip" % (w1.max() / 1.0e-3))
print("growth rate fitted over t < t_flip: %.4f   (theory %.4f)" % (fitted, lam))
print("the other two axes keep the perturbation at its initial size (growth = 1)")

fig, ax = plt.subplots(1, 3, figsize=(13.0, 4.0))
for k, lab in enumerate(("omega1", "omega2", "omega3")):
    ax[0].plot(ts_mid, ws_mid[:, k], lw=1.0, label=lab)
ax[0].axvline(t_flip_mid, color="gray", lw=0.8)
ax[0].set_xlabel("t")
ax[0].set_ylabel("angular velocity")
ax[0].set_title("start near the middle axis")
ax[0].legend(fontsize=8)

ts3, ws3 = results["about axis 3 (largest I)"]
for k, lab in enumerate(("omega1", "omega2", "omega3")):
    ax[1].plot(ts3, ws3[:, k], lw=1.0, label=lab)
ax[1].set_xlabel("t")
ax[1].set_ylabel("angular velocity")
ax[1].set_title("start near the largest axis")
ax[1].legend(fontsize=8)

ax[2].semilogy(ts_mid[mask], w1[mask], "k-", label="|omega1|")
ax[2].semilogy(ts_mid[mask], 1.0e-3 * np.cosh(lam * ts_mid[mask]), "r--", lw=1.0,
               label="cosh(%.3f t)" % lam)
ax[2].set_xlabel("t")
ax[2].set_ylabel("|omega1|")
ax[2].set_title("exponential growth")
ax[2].legend(fontsize=8)
fig.tight_layout()
plt.show()
