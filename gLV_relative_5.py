from numba import njit

@njit
def gLV_relative(X, t, theta):
        x, y, z, v, w, n = X
        r1, r2, r3, r4, r5, b12, b13, b14, b15, b21, b23, b24, b25, b31, b32, b34, b35, b41, b42, b43, b45, b51, b52, b53, b54, x0, y0, z0, v0, w0, n0 = theta
        dn_dt = r1 * x * n + b12 * x * y * n * n + b13 * x * z * n * n + b14 * x * v * n * n + b15 * x * w * n * n + r2 * y * n + b21 * x * y * n * n + b23 * y * z * n * n + b24 * y * v * n * n + b25 * y * w * n * n + r3 * z * n + b31 * x * z * n * n + b32 * y * z * n * n + b34 * z * v * n * n + b35 * z * w * n * n + r4 * v * n + b41 * v * x * n * n + b42 * v * y * n * n + b43 * v * z * n * n + b45 * v * w * n * n + r5 * w * n + b51 * w * x * n * n + b52 * w * y * n * n + b53 * w * z * n * n + b54 * w * v * n * n
        dx_dt = (r1 * x * n + b12 * x * y * n * n + b13 * x * z * n * n + b14 * x * v * n * n + b15 * x * w * n * n - x * dn_dt) / n
        dy_dt = (r2 * y * n + b21 * x * y * n * n + b23 * y * z * n * n + b24 * y * v * n * n + b25 * y * w * n * n - y * dn_dt) / n
        dz_dt = (r3 * z * n + b31 * x * z * n * n + b32 * y * z * n * n + b34 * z * v * n * n + b35 * z * w * n * n - z * dn_dt) / n
        dv_dt = (r4 * v * n + b41 * v * x * n * n + b42 * v * y * n * n + b43 * v * z * n * n + b45 * v * w * n * n - v * dn_dt) / n
        dw_dt = (r5 * w * n + b51 * w * x * n * n + b52 * w * y * n * n + b53 * w * z * n * n + b54 * w * v * n * n - w * dn_dt) / n
        return [dx_dt, dy_dt, dz_dt, dv_dt, dw_dt, dn_dt]
