import numpy as np
I = np.array([1.0, 2.0, 3.0])
def rhs(w):
    w1, w2, w3 = w
    return np.array([(I[1]-I[2])*w2*w3/I[0], (I[2]-I[0])*w3*w1/I[1], (I[0]-I[1])*w1*w2/I[2]])
w = np.array([1.0e-3, 1.0, 0.0]); dt = 1.0e-3
for i in range(40000):
    k1 = rhs(w); k2 = rhs(w+0.5*dt*k1); k3 = rhs(w+0.5*dt*k2); k4 = rhs(w+dt*k3)
    w = w + dt/6.0*(k1+2*k2+2*k3+k4)
    if i % 4000 == 0:
        L2 = np.dot(I*w, I*w); T = 0.5*np.dot(w, I*w)
        print("t=%6.1f w=(%+.4e, %+.4f, %+.4e)  L2=%.8f T=%.8f" % ((i+1)*dt, w[0], w[1], w[2], L2, T))
