import numpy as np
m, w0, beta = 1.0, 1.0, 0.1
def U(x): return 0.5*m*w0**2*x**2 + beta*x**4
def force(x): return -(m*w0**2*x + 4.0*beta*x**3)
# simple check of the crossing bookkeeping
x, v, dt, t = 0.92418, 0.0, 1.0e-4, 0.0
x_prev = x
cross = []
for i in range(200000):
    k1x, k1v = v, force(x)/m
    k2x, k2v = v + 0.5*dt*k1v, force(x + 0.5*dt*k1x)/m
    k3x, k3v = v + 0.5*dt*k2v, force(x + 0.5*dt*k2x)/m
    k4x, k4v = v + dt*k3v, force(x + dt*k3x)/m
    x_new = x + dt/6.0*(k1x + 2*k2x + 2*k3x + k4x)
    v = v + dt/6.0*(k1v + 2*k2v + 2*k3v + k4v)
    t += dt
    if x_prev < 0.0 <= x_new: cross.append(t)
    x_prev = x; x = x_new
print("n crossings", len(cross), "first", cross[:6])
print("diffs", np.diff(cross[:6]))
print("x range", x, v)
