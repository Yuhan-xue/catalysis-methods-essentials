# lab03_kepler.py --- two-body orbit with velocity-Verlet, Kepler II and III
# Units: G*(m1+m2) = 1, initial separation = 1. Depends on numpy, matplotlib.
import numpy as np
import matplotlib.pyplot as plt

mu = 1.0
r0 = np.array([1.0, 0.0])
dt = 1.0e-3


def acc(r):
    return -mu * r / np.linalg.norm(r) ** 3


def run(v0, tmax):
    r = r0.copy()
    v = np.array([0.0, v0])
    a = acc(r)
    t = 0.0
    samples = []
    peri = [0.0]
    rdot_prev = np.dot(r, v)
    energy0 = 0.5 * np.dot(v, v) - mu / np.linalg.norm(r)
    h0 = r[0] * v[1] - r[1] * v[0]
    rmax_dev, hmax_dev, emax_dev = 0.0, 0.0, 0.0
    emax_first, emax_second = 0.0, 0.0
    for _ in range(int(tmax / dt)):
        r_new = r + v * dt + 0.5 * a * dt ** 2       # velocity-Verlet
        a_new = acc(r_new)
        v = v + 0.5 * (a + a_new) * dt
        r, a = r_new, a_new
        t += dt
        h = r[0] * v[1] - r[1] * v[0]
        e = 0.5 * np.dot(v, v) - mu / np.linalg.norm(r)
        hmax_dev = max(hmax_dev, abs(h - h0))
        emax_dev = max(emax_dev, abs(e - energy0))
        if t < 0.5 * tmax:
            emax_first = max(emax_first, abs(e - energy0))
        else:
            emax_second = max(emax_second, abs(e - energy0))
        rmax_dev = max(rmax_dev, abs(np.dot(r, v)))
        rdot = np.dot(r, v)
        if rdot_prev < 0.0 and rdot >= 0.0:          # periapsis passage
            peri.append(t - dt * rdot / (rdot - rdot_prev))
        rdot_prev = rdot
        if len(samples) < 200000:
            samples.append((r[0], r[1]))
    return dict(t=t, peri=peri, samples=np.array(samples),
                h=h0, dh=hmax_dev, dE=emax_dev, drdot=rmax_dev,
                dE_first=emax_first, dE_second=emax_second)


print("reference orbit: v0 = 0.8, r0 = 1 gives a = %.6f, e = %.6f"
      % (1.0 / (2.0 - 0.8 ** 2), abs(1.0 - 1.0 / (2.0 - 0.8 ** 2)) / (1.0 / (2.0 - 0.8 ** 2))))
res = run(0.8, 12.0)
T_num = res["peri"][-1] - res["peri"][-2]
a_num = 1.0 / (2.0 - 0.8 ** 2)
print("Kepler II : |dh/h| = %.3e   (areal velocity drift)" % (res["dh"] / abs(res["h"])))
print("energy    : |dE/E| = %.3e over the first half, %.3e over the second half"
      % (res["dE_first"] / abs(0.5 * 0.8 ** 2 - 1.0), res["dE_second"] / abs(0.5 * 0.8 ** 2 - 1.0)))
print("Kepler III: T_num = %.6f, T_theory = %.6f, rel. error = %.3e"
      % (T_num, 2.0 * np.pi * a_num ** 1.5, abs(T_num - 2.0 * np.pi * a_num ** 1.5) / T_num))
print("")
print("%8s %10s %10s %10s %12s" % ("v0", "a_theory", "T_num", "T_theory", "T^2/a^3"))
vs, Ts, As = [], [], []
for v0 in (0.5, 0.7, 0.9, 1.05, 1.2):
    r = run(v0, 40.0)
    T = r["peri"][-1] - r["peri"][-2]
    a = 1.0 / (2.0 - v0 ** 2)
    print("%8.2f %10.5f %10.5f %10.5f %12.5f"
          % (v0, a, T, 2.0 * np.pi * a ** 1.5, T ** 2 / a ** 3))
    vs.append(v0)
    Ts.append(T)
    As.append(a)

slope, intercept = np.polyfit(np.log(As), np.log(Ts), 1)
print("fit: log T = %.4f * log a + %.4f   (Kepler III predicts slope 1.5, 4*pi^2 = %.4f)"
      % (slope, intercept, 4.0 * np.pi ** 2))

fig, ax = plt.subplots(1, 2, figsize=(11.0, 4.4))
for v0, style in ((0.5, "b-"), (0.8, "k-"), (1.2, "r-")):
    r = run(v0, 30.0)
    ax[0].plot(r["samples"][:, 0], r["samples"][:, 1], style, lw=0.9, label="v0 = %.2f" % v0)
ax[0].plot([0.0], [0.0], "ko", ms=6)
ax[0].set_aspect("equal")
ax[0].set_xlabel("x (length unit)")
ax[0].set_ylabel("y (length unit)")
ax[0].set_title("bound orbits, focus at origin")
ax[0].legend()
ax[1].loglog(As, Ts, "ko", label="measured")
aa = np.linspace(0.5, 2.0, 50)
ax[1].loglog(aa, 2.0 * np.pi * aa ** 1.5, "r-", label="$T=2\\pi a^{3/2}$")
ax[1].set_xlabel("semi-major axis a")
ax[1].set_ylabel("period T")
ax[1].set_title("Kepler third law")
ax[1].legend()
fig.tight_layout()
plt.show()
