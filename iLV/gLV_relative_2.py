from numba import njit
import warnings
warnings.filterwarnings('ignore')

@njit
def gLV_relative(X, t, theta):
		x1, x2, n = X
		r1, r2, b12, b21, x10, x20, n0 = theta
		dn_dt = (r1 * x1 * n) + (b12 * x1 * x2 * n * n) + (r2 * x2 * n) + (b21 * x2 * x1 * n * n)
		dx1_dt = ((r1 * x1 * n) + (b12 * x1 * x2 * n * n) - (x1 * dn_dt)) / n
		dx2_dt = ((r2 * x2 * n) + (b21 * x2 * x1 * n * n) - (x2 * dn_dt)) / n
		return [dx1_dt, dx2_dt, dn_dt]