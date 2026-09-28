# lab07_chaos.py —— 受迫杜芬振子：庞加莱截面与初值敏感性
# x'' + delta*x' + alpha*x + beta*x^3 = gamma*cos(omega*t)
# 依赖：numpy, matplotlib
import numpy as np
import matplotlib.pyplot as plt

delta, alpha, beta, gamma, omega = 0.15, -1.0, 1.0, 0.3, 1.2
Tdrive = 2.0 * np.pi / omega
steps_per_period = 200
dt = Tdrive / steps_per_period


def accel(x, v, t):
    return -delta * v - alpha * x - beta * x ** 3 + gamma * np.cos(omega * t)


def rk4_step(x, v, t, h):
    k1x, k1v = v, accel(x, v, t)
    k2x, k2v = v + 0.5 * h * k1v, accel(x + 0.5 * h * k1x, v + 0.5 * h * k1v, t + 0.5 * h)
    k3x, k3v = v + 0.5 * h * k2v, accel(x + 0.5 * h * k2x, v + 0.5 * h * k2v, t + 0.5 * h)
    k4x, k4v = v + h * k3v, accel(x + h * k3x, v + h * k3v, t + h)
    return x + h / 6.0 * (k1x + 2.0 * k2x + 2.0 * k3x + k4x), \
           v + h / 6.0 * (k1v + 2.0 * k2v + 2.0 * k3v + k4v)


def trajectory(x0, v0, n_periods, h=dt):
    n = int(round(n_periods * Tdrive / h))
    x, v, t = x0, v0, 0.0
    xs, vs = [x], [v]
    for _ in range(n):
        x, v = rk4_step(x, v, t, h)
        t += h
        xs.append(x)
        vs.append(v)
    return np.array(xs), np.array(vs)


def poincare(x0, v0, n_periods, n_transient=200):
    # 频闪截面：每跑满一个驱动周期取一个点
    n = int(round(n_periods * Tdrive / dt))
    x, v, t = x0, v0, 0.0
    px, pv = [], []
    for i in range(n):
        x, v = rk4_step(x, v, t, dt)
        t += dt
        if (i + 1) % steps_per_period == 0 and (i + 1) // steps_per_period > n_transient:
            px.append(x)
            pv.append(v)
    return np.array(px), np.array(pv)


# --- 1. 初值敏感性：两条相差 1e-8 的轨道 ---
x1, v1 = trajectory(0.10, 0.0, 120.0)
x2, v2 = trajectory(0.10 + 1.0e-8, 0.0, 120.0)
sep = np.abs(x2 - x1)
sep = np.maximum(sep, 1.0e-16)
tt = np.arange(len(sep)) * dt
t_sat = tt[np.argmax(sep > 1.0e-2)]
mask = (sep > 1.0e-9) & (tt < t_sat)          # 只在饱和之前做拟合
p = np.polyfit(tt[mask], np.log(sep[mask]), 1)
slope = p[0]
print("initial separation 1e-8 m")
print("separation reaches 1e-2 m after %.2f drive periods" % (t_sat / Tdrive))
print("fitted Lyapunov exponent lambda = %.4f per unit time" % slope)
print("theoretical estimate ln(1e6)/t_sat = %.4f" % (np.log(1.0e6) / t_sat))

# --- 2. 数值精度：步长减半，比较前 5 个周期 ---
xa, _ = trajectory(0.10, 0.0, 5.0, h=dt)
xb, _ = trajectory(0.10, 0.0, 5.0, h=dt / 2.0)
nmin = min(len(xa), len(xb))
print("max|x(dt) - x(dt/2)| over 5 periods = %.3e" % np.max(np.abs(xa[:nmin] - xb[::2][:nmin])))

# --- 3. 庞加莱截面 ---
px_c, pv_c = poincare(0.10, 0.0, 1500)
print("chaotic section: %d points, occupied x range [%.3f, %.3f]" % (px_c.size, px_c.min(), px_c.max()))

fig, ax = plt.subplots(1, 3, figsize=(13.0, 4.0))
ax[0].semilogy(tt, sep, "k-", lw=0.8)
ax[0].semilogy(tt[mask], np.exp(np.polyval(p, tt[mask])), "r--", lw=1.0,
               label="exp(%.3f t)" % slope)
ax[0].set_xlabel("t")
ax[0].set_ylabel("|dx| (m)")
ax[0].set_title("two nearby starts diverge")
ax[0].legend(fontsize=8)

xr, vr = trajectory(0.10, 0.0, 40.0)
ax[1].plot(xr, vr, "k-", lw=0.6)
ax[1].set_xlabel("x")
ax[1].set_ylabel("v")
ax[1].set_title("phase portrait (40 periods)")

ax[2].plot(px_c, pv_c, "k.", ms=1.5)
ax[2].set_xlabel("x at t = 2*pi*n/omega")
ax[2].set_ylabel("v at the same instants")
ax[2].set_title("stroboscopic Poincare section")
fig.tight_layout()
plt.show()
