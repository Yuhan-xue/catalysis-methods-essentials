# Probe: for which driving amplitude is the forced Duffing oscillator chaotic?
import numpy as np

delta, alpha, beta, omega = 0.15, -1.0, 1.0, 1.2
Tdrive = 2.0 * np.pi / omega
steps = 200
dt = Tdrive / steps


def make(gamma):
    def accel(x, v, t):
        return -delta * v - alpha * x - beta * x ** 3 + gamma * np.cos(omega * t)
    return accel


def rk4(x, v, t, h, f):
    k1x, k1v = v, f(x, v, t)
    k2x, k2v = v + 0.5 * h * k1v, f(x + 0.5 * h * k1x, v + 0.5 * h * k1v, t + 0.5 * h)
    k3x, k3v = v + 0.5 * h * k2v, f(x + 0.5 * h * k2x, v + 0.5 * h * k2v, t + 0.5 * h)
    k4x, k4v = v + h * k3v, f(x + h * k3x, v + h * k3v, t + h)
    return x + h / 6.0 * (k1x + 2.0 * k2x + 2.0 * k3x + k4x), \
           v + h / 6.0 * (k1v + 2.0 * k2v + 2.0 * k3v + k4v)


def lyap(gamma, nper=120):
    f = make(gamma)
    x1, v1, x2, v2, t = 0.1, 0.0, 0.1 + 1e-8, 0.0, 0.0
    n = int(round(nper * Tdrive / dt))
    sep = []
    for _ in range(n):
        x1, v1 = rk4(x1, v1, t, dt, f)
        x2, v2 = rk4(x2, v2, t, dt, f)
        t += dt
        sep.append(abs(x2 - x1))
    sep = np.maximum(np.array(sep), 1e-16)
    tt = np.arange(len(sep)) * dt
    if np.any(sep > 1e-2):
        tsat = tt[np.argmax(sep > 1e-2)]
    else:
        tsat = tt[-1]                     # never saturates: regular motion
    m = (sep > 1e-9) & (tt < tsat)
    return np.polyfit(tt[m], np.log(sep[m]), 1)[0], tsat


def section_size(gamma, nper=1500, ntrans=200):
    f = make(gamma)
    x, v, t = 0.1, 0.0, 0.0
    px, pv = [], []
    n = int(round(nper * Tdrive / dt))
    for i in range(n):
        x, v = rk4(x, v, t, dt, f)
        t += dt
        if (i + 1) % steps == 0 and (i + 1) // steps > ntrans:
            px.append(x)
            pv.append(v)
    px, pv = np.array(px), np.array(pv)
    bins = set(zip(np.round(px / 0.05).astype(int), np.round(pv / 0.05).astype(int)))
    return len(px), len(bins)


for g in (0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5):
    lam, tsat = lyap(g)
    npt, nbin = section_size(g)
    print("gamma = %.2f   lambda = %+.4f (saturates at t = %.1f periods)   section: %d points in %d bins"
          % (g, lam, tsat / Tdrive, npt, nbin))
