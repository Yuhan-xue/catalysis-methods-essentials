x, v, dt, t = -3.0e-4, 1.0, 1.0e-4, 0.0
x_prev = x
for i in range(6):
    k1x, k1v = v, 0.0
    k2x, k2v = v + 0.5*dt*k1v, 0.0
    k3x, k3v = v + 0.5*dt*k2v, 0.0
    k4x, k4v = v + dt*k3v, 0.0
    x_new = x + dt/6.0*(k1x + 2*k2x + 2*k3x + k4x)
    v = v + dt/6.0*(k1v + 2*k2v + 2*k3v + k4v)
    t += dt
    print("i=%d t=%.1e x_before=%+.6e x_new=%+.6e fire=%s" % (i, t, x, x_new, x_prev < 0.0 <= x_new))
    x_prev = x
    x = x_new
