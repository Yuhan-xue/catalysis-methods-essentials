# lab11_energy_drift.py —— 显式欧拉 / RK4 / 辛欧拉的能量漂移对比
# 简谐振动 x'' = -w0^2 x，w0 = 2*pi rad/s（周期正好 1 s）
# 依赖：numpy, matplotlib
import numpy as np
import matplotlib.pyplot as plt

w0 = 2.0 * np.pi
x0, v0 = 1.0, 0.0
E0 = 0.5 * (v0 ** 2 + w0 ** 2 * x0 ** 2)


def run(method, h, tend):
    n = int(round(tend / h))
    x, v = x0, v0
    xs = np.empty(n + 1)
    Es = np.empty(n + 1)
    xs[0] = x
    Es[0] = 0.5 * (v ** 2 + w0 ** 2 * x ** 2)
    for i in range(n):
        if method == "euler":                       # 显式（前向）欧拉
            x, v = x + h * v, v - h * w0 ** 2 * x
        elif method == "ec":                        # 辛欧拉（Euler-Cromer）
            v = v - h * w0 ** 2 * x
            x = x + h * v
        else:                                       # 经典 RK4
            k1x, k1v = v, -w0 ** 2 * x
            k2x, k2v = v + 0.5 * h * k1v, -w0 ** 2 * (x + 0.5 * h * k1x)
            k3x, k3v = v + 0.5 * h * k2v, -w0 ** 2 * (x + 0.5 * h * k2x)
            k4x, k4v = v + h * k3v, -w0 ** 2 * (x + h * k3x)
            x = x + h / 6.0 * (k1x + 2.0 * k2x + 2.0 * k3x + k4x)
            v = v + h / 6.0 * (k1v + 2.0 * k2v + 2.0 * k3v + k4v)
        xs[i + 1] = x
        Es[i + 1] = 0.5 * (v ** 2 + w0 ** 2 * x ** 2)
    return np.linspace(0.0, n * h, n + 1), xs, Es


print("omega0 = %.4f rad/s, period = 1.000 s, E0 = %.6f J" % (w0, E0))
print("")
for method, name in (("euler", "explicit Euler"), ("rk4", "RK4"), ("ec", "symplectic Euler")):
    print(name)
    print("%10s %15s %15s %15s" % ("h/s", "E/E0 at 1 s", "E/E0 at 5 s", "E/E0 at 10 s"))
    for h in (0.1, 0.01, 0.001):
        ts, xs, Es = run(method, h, 10.0)
        print("%10.3f %15.6e %15.6e %15.6e"
              % (h, np.interp(1.0, ts, Es) / E0, np.interp(5.0, ts, Es) / E0, Es[-1] / E0))
    print("")

print("explicit Euler obeys E_n/E_0 = (1 + omega0^2 h^2)^n exactly")
print("%10s %20s %20s" % ("h/s", "predicted at 10 s", "measured at 10 s"))
for h in (0.1, 0.01, 0.001):
    ts, xs, Es = run("euler", h, 10.0)
    print("%10.3f %20.6e %20.6e"
          % (h, (1.0 + w0 ** 2 * h ** 2) ** int(round(10.0 / h)), Es[-1] / E0))
print("")

print("order of accuracy in the small-error regime")
hs_e = np.array([1.0e-2, 3.0e-3, 1.0e-3, 3.0e-4, 1.0e-4])
err_e = np.array([abs(run("euler", h, 1.0)[2][-1] / E0 - 1.0) for h in hs_e])
slope_e = np.polyfit(np.log(hs_e), np.log(err_e), 1)[0]
print("  Euler at t = 1 s: fitted slope %.3f   (small-h limit = 1)" % slope_e)
hs_r = np.array([0.1, 0.05, 0.02, 0.01])
err_r = np.array([abs(run("rk4", h, 10.0)[2][-1] / E0 - 1.0) for h in hs_r])
slope_r = np.polyfit(np.log(hs_r), np.log(err_r), 1)[0]
print("  RK4 at t = 10 s: fitted slope %.3f   (accumulated energy loss scales as h^5)" % slope_r)
print("  RK4 loss per step is (h*omega0)^6/72, so after t/h steps it is t*h^5*omega0^6/72")
for h in hs_r:
    pred = 10.0 * h ** 5 * w0 ** 6 / 72.0
    meas = abs(run("rk4", h, 10.0)[2][-1] / E0 - 1.0)
    print("    h = %.3f s   predicted %.4e   measured %.4e" % (h, pred, meas))
print("")

print("max |dE/E| over 200 s at h = 0.01 s")
for method, name in (("euler", "explicit Euler"), ("rk4", "RK4"), ("ec", "symplectic Euler")):
    ts, xs, Es = run(method, 0.01, 200.0)
    print("  %-16s max |dE/E| = %.4e   final E/E0 = %.4e"
          % (name, np.max(np.abs(Es / E0 - 1.0)), Es[-1] / E0))

fig, ax = plt.subplots(1, 3, figsize=(13.0, 4.0))
ts, xs, Es = run("euler", 0.1, 3.0)
ax[0].plot(ts, xs, "r-", lw=1.2, label="Euler, h = 0.1 s")
ts, xs, Es = run("rk4", 0.1, 3.0)
ax[0].plot(ts, xs, "k-", lw=1.2, label="RK4, h = 0.1 s")
ax[0].plot(ts, np.cos(w0 * ts), "b--", lw=0.9, label="analytic")
ax[0].set_ylim(-4.0, 4.0)
ax[0].set_xlabel("t (s)")
ax[0].set_ylabel("x (m)")
ax[0].set_title("same step, different fate")
ax[0].legend(fontsize=8)

for h, col in ((0.1, "r"), (0.01, "g"), (0.001, "b")):
    ts, xs, Es = run("euler", h, 10.0)
    ax[1].semilogy(ts, np.abs(Es / E0 - 1.0) + 1.0e-16, col + "-", lw=1.0,
                   label="Euler h = %g s" % h)
    ts, xs, Es = run("rk4", h, 10.0)
    ax[1].semilogy(ts, np.abs(Es / E0 - 1.0) + 1.0e-16, col + "--", lw=1.0,
                   label="RK4 h = %g s" % h)
ax[1].set_xlabel("t (s)")
ax[1].set_ylabel("|dE/E|")
ax[1].set_title("energy drift")
ax[1].legend(fontsize=7)

ax[2].loglog(hs_e, err_e, "ro-", label="Euler, slope %.2f" % slope_e)
ax[2].loglog(hs_r, err_r, "ks-", label="RK4, slope %.2f" % slope_r)
hs_c = np.array([0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001])
err_c = np.array([max(abs(run("ec", h, 10.0)[2] / E0 - 1.0)) for h in hs_c])
ax[2].loglog(hs_c, err_c, "b^-", label="symplectic Euler")
ax[2].set_xlabel("step h (s)")
ax[2].set_ylabel("|dE/E|")
ax[2].set_title("order of accuracy")
ax[2].legend(fontsize=8)
fig.tight_layout()
plt.show()
