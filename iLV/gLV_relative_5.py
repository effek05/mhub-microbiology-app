from numba import njit
import warnings
warnings.filterwarnings('ignore')

@njit
def gLV_relative(X, t, theta):
		x1, x2, x3, x4, x5, n = X
		r1, r2, r3, r4, r5, b12, b13, b14, b15, b21, b23, b24, b25, b31, b32, b34, b35, b41, b42, b43, b45, b51, b52, b53, b54, x10, x20, x30, x40, x50, n0 = theta
		dn_dt = (r1 * x1 * n) + (b12 * x1 * x2 * n * n) + (b13 * x1 * x3 * n * n) + (b14 * x1 * x4 * n * n) + (b15 * x1 * x5 * n * n) + (r2 * x2 * n) + (b21 * x2 * x1 * n * n) + (b23 * x2 * x3 * n * n) + (b24 * x2 * x4 * n * n) + (b25 * x2 * x5 * n * n) + (r3 * x3 * n) + (b31 * x3 * x1 * n * n) + (b32 * x3 * x2 * n * n) + (b34 * x3 * x4 * n * n) + (b35 * x3 * x5 * n * n) + (r4 * x4 * n) + (b41 * x4 * x1 * n * n) + (b42 * x4 * x2 * n * n) + (b43 * x4 * x3 * n * n) + (b45 * x4 * x5 * n * n) + (r5 * x5 * n) + (b51 * x5 * x1 * n * n) + (b52 * x5 * x2 * n * n) + (b53 * x5 * x3 * n * n) + (b54 * x5 * x4 * n * n)
		dx1_dt = ((r1 * x1 * n) + (b12 * x1 * x2 * n * n) + (b13 * x1 * x3 * n * n) + (b14 * x1 * x4 * n * n) + (b15 * x1 * x5 * n * n) - (x1 * dn_dt)) / n
		dx2_dt = ((r2 * x2 * n) + (b21 * x2 * x1 * n * n) + (b23 * x2 * x3 * n * n) + (b24 * x2 * x4 * n * n) + (b25 * x2 * x5 * n * n) - (x2 * dn_dt)) / n
		dx3_dt = ((r3 * x3 * n) + (b31 * x3 * x1 * n * n) + (b32 * x3 * x2 * n * n) + (b34 * x3 * x4 * n * n) + (b35 * x3 * x5 * n * n) - (x3 * dn_dt)) / n
		dx4_dt = ((r4 * x4 * n) + (b41 * x4 * x1 * n * n) + (b42 * x4 * x2 * n * n) + (b43 * x4 * x3 * n * n) + (b45 * x4 * x5 * n * n) - (x4 * dn_dt)) / n
		dx5_dt = ((r5 * x5 * n) + (b51 * x5 * x1 * n * n) + (b52 * x5 * x2 * n * n) + (b53 * x5 * x3 * n * n) + (b54 * x5 * x4 * n * n) - (x5 * dn_dt)) / n
		return [dx1_dt, dx2_dt, dx3_dt, dx4_dt, dx5_dt, dn_dt]