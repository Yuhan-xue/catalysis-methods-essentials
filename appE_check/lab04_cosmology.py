# lab04_cosmology.py --- matter era to dark-energy era, Planck 2018 parameters
# Depends on numpy, matplotlib.
import numpy as np
import matplotlib.pyplot as plt

H0_kmsMpc = 67.4                       # km/s/Mpc, Planck 2018
Mpc_m = 3.0856775814913673e22          # m
H0 = H0_kmsMpc * 1.0e3 / Mpc_m         # 1/s
Om, OL = 0.315, 0.685                  # flat LCDM
Gyr = 3.15576e16                       # s in one Julian gigayear


def E(a):
    return np.sqrt(Om / a ** 3 + OL)


def trapz(y, x):
    # 手写梯形积分，避免依赖 numpy 2.0 才有的 np.trapezoid
    return np.sum(0.5 * (y[1:] + y[:-1]) * np.diff(x))


def dadt(a):
    return H0 * a * E(a)


# --- 1. age of the universe: t0 = int da / (a H(a)), integrate in x = ln a ---
x = np.linspace(-30.0, 0.0, 400001)
integrand = 1.0 / np.sqrt(Om * np.exp(-3.0 * x) + OL)
t0 = trapz(integrand, x) / H0
print("Hubble time 1/H0 = %.4f Gyr" % (1.0 / H0 / Gyr))
print("age of the universe = %.4f Gyr   (Planck 2018: 13.797 Gyr)" % (t0 / Gyr))

# --- 2. a(t) by RK4, starting deep in the matter era ---
a0, tmax = 1.0e-3, 0.0
a = a0
t = 0.0
dt = 1.0e-5 * (1.0 / H0)               # small compared with 1/H0
ts, as_ = [0.0], [a]
while a < 1.35:
    k1 = dadt(a)
    k2 = dadt(a + 0.5 * dt * k1)
    k3 = dadt(a + 0.5 * dt * k2)
    k4 = dadt(a + dt * k3)
    a += dt / 6.0 * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    t += dt
    ts.append(t)
    as_.append(a)
ts = np.array(ts) / Gyr
as_ = np.array(as_)
print("a = 1 reached at cosmic time %.4f Gyr" % np.interp(1.0, as_, ts))

# --- 3. characteristic epochs ---
a_eq = (Om / OL) ** (1.0 / 3.0)        # matter density equals dark energy
a_acc = (Om / (2.0 * OL)) ** (1.0 / 3.0)   # deceleration turns into acceleration
print("matter/dark-energy equality: a = %.4f  (z = %.3f)" % (a_eq, 1.0 / a_eq - 1.0))
print("acceleration begins at a = %.4f  (z = %.3f), t = %.3f Gyr"
      % (a_acc, 1.0 / a_acc - 1.0, np.interp(a_acc, as_, ts)))
print("")
print("%8s %10s %10s %12s" % ("a", "H(a)/H0", "q(a)", "t / Gyr"))
for av in (0.01, 0.1, 0.5, a_eq, 0.9, 1.0, 1.3):
    q = (0.5 * Om / av ** 3 - OL) / E(av) ** 2
    print("%8.4f %10.4f %10.4f %12.4f" % (av, E(av), q, np.interp(av, as_, ts)))

fig, ax = plt.subplots(1, 3, figsize=(13.0, 3.9))
ax[0].plot(ts, as_, "k-", lw=1.6)
ax[0].axhline(1.0, color="gray", lw=0.8)
ax[0].axvline(np.interp(a_acc, as_, ts), color="r", ls="--", lw=0.9)
ax[0].set_xlim(0.0, 25.0)
ax[0].set_xlabel("t (Gyr)")
ax[0].set_ylabel("scale factor a")
ax[0].set_title("scale factor grows without bound")

av = np.logspace(-2.0, 0.4, 400)
ax[1].loglog(av, E(av), "k-")
ax[1].loglog(av, np.sqrt(Om) * av ** -1.5, "b--", lw=0.9, label="$a^{-3/2}$ (matter)")
ax[1].loglog(av, np.sqrt(OL) * np.ones_like(av), "r--", lw=0.9, label="constant (dark energy)")
ax[1].axvline(a_eq, color="gray", lw=0.8)
ax[1].set_xlabel("a")
ax[1].set_ylabel("H(a)/H0")
ax[1].set_title("who dominates")
ax[1].legend()

q = (0.5 * Om / av ** 3 - OL) / E(av) ** 2
ax[2].plot(av, q, "k-")
ax[2].axhline(0.0, color="gray", lw=0.8)
ax[2].axvline(a_acc, color="r", ls="--", lw=0.9)
ax[2].set_xlim(0.0, 2.0)
ax[2].set_ylim(-1.0, 0.6)
ax[2].set_xlabel("a")
ax[2].set_ylabel("deceleration parameter q")
ax[2].set_title("deceleration turns negative")
fig.tight_layout()
plt.show()
