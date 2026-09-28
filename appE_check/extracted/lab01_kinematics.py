# lab01_kinematics.py —— 数值微分与数值积分
# 给定 a(t)，求 v(t) 与 x(t)；再用差分从 x(t) 还原 v 与 a
# 依赖：numpy, matplotlib
import numpy as np
import matplotlib.pyplot as plt


def a_exact(t):
    return 2.0 - 0.5 * t + 0.3 * np.sin(t)          # m/s^2，给定的加速度


def v_exact(t):
    return 2.0 * t - 0.25 * t ** 2 - 0.3 * np.cos(t) + 0.3   # m/s，取 v(0)=0


def x_exact(t):
    return t ** 2 - t ** 3 / 12.0 - 0.3 * np.sin(t) + 0.3 * t  # m，取 x(0)=0


T, N = 10.0, 2000
t = np.linspace(0.0, T, N + 1)
dt = t[1] - t[0]
a = a_exact(t)

v = np.zeros_like(t)                  # 梯形法积分
for i in range(N):
    v[i + 1] = v[i] + 0.5 * (a[i] + a[i + 1]) * dt

v_rect = np.zeros_like(t)             # 左矩形法积分
for i in range(N):
    v_rect[i + 1] = v_rect[i] + a[i] * dt

x = np.zeros_like(t)                  # 再积分一次得到位置
for i in range(N):
    x[i + 1] = x[i] + 0.5 * (v[i] + v[i + 1]) * dt

x_euler = np.zeros_like(t)            # 显式欧拉法，作为反面教材
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
    vv = (xx[2:] - xx[:-2]) / (2.0 * h)                     # 一阶中心差分
    aa = (xx[2:] - 2.0 * xx[1:-1] + xx[:-2]) / h ** 2       # 二阶中心差分
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
