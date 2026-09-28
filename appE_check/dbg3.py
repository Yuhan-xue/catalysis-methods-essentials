import numpy as np
m, k = 1.0, 1.0
def force(x): return -k*x
x, v, dt, t = 1.0, 0.0, 1.0e-3, 0.0
x_prev = x
cross = []
for i in range(20000):
    k1x, k1v = v, force(x)/m
    k2x, k2v = v + 0.5*dt*k1v, force(x + 0.5*dt*k1x)/m
    k3x, k3v = v + 0.5*dt*k2v, force(x + 0.5*dt*k2x)/m
    k4x, k4v = v + dt*k3v, force(x + dt*k3x)/m
    x_new = x + dt/6.0*(k1x + 2*k2x + 2*k3x + k4x)
    v = v + dt/6.0*(k1v + 2*k2v + 2*k3v + k4v)
    t += dt
    if x_prev < 0.0 <= x_new:
        cross.append(t - dt*x_new/(x_new-x_prev))
    x_prev = x; x = x_new
print("analytic x(20) = %.10f   numeric = %.10f" % (np.cos(20.0), x))
print("crossings:", cross[:6])
print("period diffs:", np.diff(cross[:6]), "vs 2pi =", 2*np.pi)
