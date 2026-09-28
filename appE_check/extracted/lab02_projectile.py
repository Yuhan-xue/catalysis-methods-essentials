# lab02_projectile.py —— 无阻力 / 线性阻力 / 二次阻力三种抛体
# 依赖：numpy, matplotlib
import numpy as np
import matplotlib.pyplot as plt

g = 9.80665           # m/s^2，CODATA 2022 标准重力加速度
v0 = 50.0             # m/s，初速率
theta = np.deg2rad(45.0)
m = 0.145             # kg，棒球质量
gamma = 0.25          # 1/s，线性阻力系数 b/m
k2 = 6.2e-3           # 1/m，二次阻力系数 (rho*Cd*A/2)/m
dt = 1.0e-3


def accel(vx, vy, mode):
    speed = np.hypot(vx, vy)
    ax, ay = 0.0, -g
    if mode == "linear":
        ax -= gamma * vx
        ay -= gamma * vy
    elif mode == "quadratic":
        ax -= k2 * speed * vx
        ay -= k2 * speed * vy
    return ax, ay


def rhs(s, mode):
    ax, ay = accel(s[2], s[3], mode)
    return np.array([s[2], s[3], ax, ay])


def integrate(mode, tmax=30.0):
    s = np.array([0.0, 0.0, v0 * np.cos(theta), v0 * np.sin(theta)])
    ts = [0.0]
    hist = [s.copy()]
    t = 0.0
    while t < tmax:
        k1 = rhs(s, mode)
        k2v = rhs(s + 0.5 * dt * k1, mode)
        k3 = rhs(s + 0.5 * dt * k2v, mode)
        k4 = rhs(s + dt * k3, mode)
        s_new = s + dt / 6.0 * (k1 + 2.0 * k2v + 2.0 * k3 + k4)
        if s_new[1] < 0.0:                      # 落地：线性插值到 y = 0
            frac = s[1] / (s[1] - s_new[1])
            s_new = s + frac * (s_new - s)
            s_new[1] = 0.0
            t += frac * dt
            ts.append(t)
            hist.append(s_new.copy())
            break
        s = s_new
        t += dt
        ts.append(t)
        hist.append(s.copy())
    return np.array(ts), np.array(hist)


print("vacuum prediction: range = %.3f m, apex = %.3f m, flight time = %.3f s"
      % (v0 ** 2 * np.sin(2.0 * theta) / g, (v0 * np.sin(theta)) ** 2 / (2.0 * g),
         2.0 * v0 * np.sin(theta) / g))
print("terminal speed: linear %.3f m/s, quadratic %.3f m/s"
      % (g / gamma, np.sqrt(g / k2)))
print("")
print("%-10s %10s %10s %10s %10s" % ("drag", "range/m", "apex/m", "flight/s", "impact/(m/s)"))
for mode in ("none", "linear", "quadratic"):
    ts, hist = integrate(mode)
    apex = hist[:, 1].max()
    print("%-10s %10.3f %10.3f %10.3f %10.3f"
          % (mode, hist[-1, 0], apex, ts[-1], np.hypot(hist[-1, 2], hist[-1, 3])))

fig, ax = plt.subplots(1, 2, figsize=(11.0, 4.2))
for mode, style in (("none", "k-"), ("linear", "b--"), ("quadratic", "r-.")):
    ts, hist = integrate(mode)
    ax[0].plot(hist[:, 0], hist[:, 1], style, label=mode)
    ax[1].plot(ts, np.hypot(hist[:, 2], hist[:, 3]), style, label=mode)
ax[0].axhline(0.0, color="gray", lw=0.8)
ax[0].set_xlabel("x (m)")
ax[0].set_ylabel("y (m)")
ax[0].set_title("trajectories")
ax[0].legend()
ax[1].set_xlabel("t (s)")
ax[1].set_ylabel("speed (m/s)")
ax[1].set_title("speed versus time")
ax[1].legend()
fig.tight_layout()
plt.show()
