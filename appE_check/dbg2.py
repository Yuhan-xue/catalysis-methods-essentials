import numpy as np
m, w0, beta = 1.0, 1.0, 0.1
def force(x): return -(m*w0**2*x + 4.0*beta*x**3)
x, v, dt, t = 0.92418, 0.0, 1.0e-4, 0.0
x_prev = x
n = 0
for i in range(50000):
    k1x, k1v = v, force(x)/m
    k2x, k2v = v + 0.5*dt*k1v, force(x + 0.5*dt*k1x)/m
    k3x, k3v = v + 0.5*dt*k2v, force(x + 0.5*dt*k2x)/m
    k4x, k4v = v + dt*k3v, force(x + dt*k3x)/m
    x_new = x + dt/6.0*(k1x + 2*k2x + 2*k3x + k4x)
    v = v + dt/6.0*(k1v + 2*k2v + 2*k3v + k4v)
    t += dt
    if 4.20 < t < 4.22:
        print("t=%.5f x_prev=%+.6e x_new=%+.6e v=%+.6e fire=%s" % (t, x_prev, x_new, v, x_prev < 0.0 <= x_new))
    if x_prev < 0.0 <= x_new: n += 1
    x_prev = x; x = x_new
print("fires", n)
