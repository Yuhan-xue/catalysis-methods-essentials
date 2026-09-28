# lab08_collision.py —— 二维碰撞：实验室系与质心系对比
# 依赖：numpy, matplotlib
import numpy as np
import matplotlib.pyplot as plt

m1, m2 = 2.0, 1.0
R = 1.0
v0 = 3.0


def simulate(b, e, tmax=6.0, dt=2.0e-4):
    r1 = np.array([-6.0, b])
    r2 = np.array([0.0, 0.0])
    v1 = np.array([v0, 0.0])
    v2 = np.array([0.0, 0.0])
    t, hits = 0.0, 0
    path1, path2 = [r1.copy()], [r2.copy()]
    while t < tmax:
        r1 = r1 + v1 * dt
        r2 = r2 + v2 * dt
        t += dt
        d = r1 - r2
        dist = np.linalg.norm(d)
        if dist <= 2.0 * R:                    # 两球接触
            n = d / dist
            vn = np.dot(v1 - v2, n)
            if vn < 0.0:                       # 正在接近：施加法向冲量
                J = -(1.0 + e) * vn / (1.0 / m1 + 1.0 / m2)
                v1 = v1 + (J / m1) * n
                v2 = v2 - (J / m2) * n
                hits += 1
        path1.append(r1.copy())
        path2.append(r2.copy())
    return np.array(path1), np.array(path2), v1, v2, hits


def reduced_energy(b, e, vn):
    mu = m1 * m2 / (m1 + m2)
    return 0.5 * mu * (1.0 - e ** 2) * vn ** 2


print("m1 = %.1f kg at %.1f m/s hits m2 = %.1f kg at rest, R = %.1f m" % (m1, v0, m2, R))
print("centre-of-mass speed V = %.4f m/s, initial KE = %.4f J"
      % (m1 * v0 / (m1 + m2), 0.5 * m1 * v0 ** 2))
print("")
print("e = 0.5, impact parameter scan")
print("%8s %10s %10s %12s %12s %12s" % ("b/m", "|p| drift", "KE_i/J", "KE_f/J", "loss/J", "theory/J"))
for b in (0.0, 0.5, 1.0, 1.5, 1.9):
    p1, p2, v1, v2, hits = simulate(b, 0.5)
    p_before = np.array([m1 * v0, 0.0])
    p_after = m1 * v1 + m2 * v2
    ke_i = 0.5 * m1 * v0 ** 2
    ke_f = 0.5 * m1 * np.dot(v1, v1) + 0.5 * m2 * np.dot(v2, v2)
    theory = reduced_energy(b, 0.5, v0 * np.sqrt(1.0 - (b / (2.0 * R)) ** 2))
    print("%8.2f %10.2e %10.4f %12.4f %12.4f %12.4f"
          % (b, np.linalg.norm(p_after - p_before), ke_i, ke_f, ke_i - ke_f, theory))
print("")
print("b = 1.0 m, restitution scan")
print("%8s %12s %12s %14s %12s" % ("e", "KE_i/J", "KE_f/J", "loss fraction", "theory"))
for e in (1.0, 0.75, 0.5, 0.25, 0.0):
    p1, p2, v1, v2, hits = simulate(1.0, e)
    ke_i = 0.5 * m1 * v0 ** 2
    ke_f = 0.5 * m1 * np.dot(v1, v1) + 0.5 * m2 * np.dot(v2, v2)
    frac = (ke_i - ke_f) / ke_i
    print("%8.2f %12.4f %12.4f %14.5f %12.5f"
          % (e, ke_i, ke_f, frac, reduced_energy(1.0, e, v0 * np.sqrt(0.75)) / ke_i))

fig, ax = plt.subplots(1, 2, figsize=(11.0, 4.4))
for b, col in ((0.0, "b"), (1.0, "r"), (1.9, "g")):
    p1, p2, v1, v2, hits = simulate(b, 0.5)
    ax[0].plot(p1[:, 0], p1[:, 1], col + "-", lw=0.9, label="m1, b = %.1f m" % b)
    ax[0].plot(p2[:, 0], p2[:, 1], col + "--", lw=0.9, label="m2, b = %.1f m" % b)
    Vcm = np.array([m1 * v0 / (m1 + m2), 0.0])
    q1 = p1 - Vcm * (np.arange(len(p1)) * 2.0e-4)[:, None]
    q2 = p2 - Vcm * (np.arange(len(p2)) * 2.0e-4)[:, None]
    ax[1].plot(q1[:, 0], q1[:, 1], col + "-", lw=0.9)
    ax[1].plot(q2[:, 0], q2[:, 1], col + "--", lw=0.9)
ax[0].set_xlabel("x (m)")
ax[0].set_ylabel("y (m)")
ax[0].set_title("laboratory frame")
ax[0].legend(fontsize=7)
ax[1].plot([0.0], [0.0], "ko", ms=5)
ax[1].set_xlabel("x' (m)")
ax[1].set_ylabel("y' (m)")
ax[1].set_title("centre-of-mass frame")
fig.tight_layout()
plt.show()
