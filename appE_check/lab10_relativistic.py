# lab10_relativistic.py --- proton in a uniform electric field, v never reaches c
# Depends on numpy, matplotlib.
import numpy as np
import matplotlib.pyplot as plt

c = 2.99792458e8                    # m/s, exact
q = 1.602176634e-19                 # C, exact
m = 1.67262192595e-27               # kg, proton
Efield = 1.0e6                      # V/m

a0 = q * Efield / (m * c)           # 1/s, the only rate in the problem
t_char = 1.0 / a0                   # s, Newtonian time to reach c
x_char = m * c ** 2 / (q * Efield)  # m, characteristic length
mc2_MeV = m * c ** 2 / 1.602176634e-13
print("proton in E = %.0e V/m" % Efield)
print("characteristic time  mc/(qE) = %.4e s = %.3f us" % (t_char, t_char * 1.0e6))
print("characteristic length mc^2/(qE) = %.3f m" % x_char)
print("rest energy mc^2 = %.3f MeV" % mc2_MeV)
print("")
print("%12s %14s %14s %12s" % ("beta", "t (ns)", "x (m)", "K (MeV)"))
for b in (0.5, 0.9, 0.99, 0.999, 0.999999):
    t = b / (a0 * np.sqrt(1.0 - b ** 2))
    x = x_char * (1.0 / np.sqrt(1.0 - b ** 2) - 1.0)
    K = (1.0 / np.sqrt(1.0 - b ** 2) - 1.0) * mc2_MeV
    print("%12.6f %14.3f %14.3f %12.4f" % (b, t * 1.0e9, x, K))
print("")
print("Newtonian mechanics predicts beta = 1 at t = %.3f us," % (t_char * 1.0e6))
print("but the relativistic beta there is %.6f" % (a0 * t_char / np.sqrt(1.0 + (a0 * t_char) ** 2)))

t = np.linspace(0.0, 4.0e-5, 400001)          # 0 to 40 us
beta = a0 * t / np.sqrt(1.0 + (a0 * t) ** 2)
gamma = 1.0 / np.sqrt(1.0 - beta ** 2)
K_MeV = (gamma - 1.0) * mc2_MeV

fig, ax = plt.subplots(1, 2, figsize=(11.0, 4.2))
ax[0].plot(t * 1.0e6, np.minimum(a0 * t, 1.2), "b--", lw=1.0, label="Newtonian beta")
ax[0].plot(t * 1.0e6, beta, "k-", lw=1.6, label="relativistic beta")
ax[0].axhline(1.0, color="r", ls=":", lw=1.0)
ax[0].axvline(t_char * 1.0e6, color="gray", lw=0.8)
ax[0].set_ylim(0.0, 1.25)
ax[0].set_xlabel("t (us)")
ax[0].set_ylabel("beta = v/c")
ax[0].set_title("speed approaches c but never reaches it")
ax[0].legend(fontsize=8)

ax[1].plot(t * 1.0e6, K_MeV, "k-", lw=1.6)
ax[1].set_xlabel("t (us)")
ax[1].set_ylabel("kinetic energy (MeV)")
ax[1].set_title("energy keeps growing")
fig.tight_layout()
plt.show()
