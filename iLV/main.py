import os
import time as tm
import numpy as np
import pandas as pd

from numba import njit
from scipy.integrate import odeint
from scipy.optimize import least_squares
from sklearn import linear_model
from scipy.optimize import leastsq

from iLV.utils import convert_to_relative_abundance
from iLV.utils import rmse
from iLV.utils import plot
from iLV.utils import plot_plate

import warnings
warnings.filterwarnings('ignore')

import random
random.seed(10)

def iLV(relative_abundance, minutes, num_run, n0_est, num_iteration, output_dir, absolute_abundance: None):
    """
    Reproducing a more generalizable version of https://github.com/willhahah/iLV/blob/main/code/Fig_5.ipynb
    Sun F, Huang Y, Tang T, Dai X (2026)
    Quantifying microbial interactions based on compositional data using an iterative approach for solving generalized Lotka-Volterra equations.
    PLoS Comput Biol 22(1): e1013876.
    https://doi.org/10.1371/journal.pcbi.1013876

    :param relative_abundance: path to relative abundance csv file -> csv shape: (time points x species), first col should be time points
    :param num_run: number of runs (to measure runtime set to 1, but set to higher number and return best results for unstable case)
    :param n0_est: initial guess of interspecies sum of absolute abundances
    :param num_iteration: number of iterations for the 1st subroutine
    :param absolute_abundance: optional: path to absolute abundance csv file
    :return: estimated parameters
    """

    if not os.path.exists(relative_abundance):
        df = convert_to_relative_abundance(absolute_abundance, relative_abundance)
    else:
        df = pd.read_csv(relative_abundance)

    timepoints = np.array(df.iloc[:, 0])
    n_tpoints = len(timepoints)
    time_seg = [timepoints[i + 1] - timepoints[i] for i in range(n_tpoints - 1)]
    # Difference between any two adjacent timepoints should be the same
    if np.unique(time_seg) == 1:
        time_seg = time_seg[0]
    else:
        exit()
    n_species = df.shape[1] - 1

    # Compare RMSE of 3 optimization methods
    min_distance = np.inf

    for k in range(num_run):

        start_time = tm.time()

        relative_dict = {f"n{i}_relative": df.iloc[:,i] for i in range(1,n_species+1)}
        real_value = pd.DataFrame(relative_dict) # (n_tpoints x n_species)
        absolute_dict = {f"n{i}_abs": df.iloc[:,i] * n0_est for i in range(1,n_species+1)}
        data = pd.DataFrame(relative_dict | absolute_dict) # (n_tpoints x n_species * 2)

        # 1st step of subroutine 1
        theta_init = linear_regression(data, n_tpoints, time_seg, n_species)
        X = np.append(np.array(real_value.iloc[0, :]), np.array(n0_est))
        theta_estimate = np.concatenate((theta_init, X))

        # 2nd step subroutine 1
        # Todo: Plot decrease in rmse over iterations
        distance =  [None] * num_iteration
        distance_min = np.inf
        theta_min = theta_estimate

        for m in range(num_iteration):
            theta = theta_estimate
            x_y_hat = odeint(func=gLV_relative, y0=theta[-(n_species+1):], t=timepoints, args=(theta,))

            distance[m] = rmse(real_value, x_y_hat[:, :-1])
            if distance[m] < distance_min:
                distance_min = distance[m]
                theta_min = theta_estimate

            data = pd.DataFrame({f"n{i}_relative": np.array(x_y_hat[:, i-1]) for i in range(1,n_species+1)} | {f"n{i}_abs": np.array(real_value.iloc[:, i-1]) * np.array(x_y_hat[:, -1]) for i in range(1,n_species+1)})

            theta_estimate = linear_regression(data, n_tpoints, time_seg, n_species)
            theta_estimate = np.concatenate((theta_estimate, X))

        # subroutine 2
        def ode_model_resid(theta):
            """
            :param thetab: Theta
            :return: Residuals based on given theta
            """
            return (np.abs(real_value - np.delete(odeint(func=gLV_relative, y0=theta[-(n_species + 1):], t=timepoints, args=(theta,)), -1, axis=1))
            ).values.flatten()

        random.seed(10)
        results_sq = leastsq(ode_model_resid, x0=theta_min)
        theta_sq = results_sq[0]

        random.seed(10)
        results_trf = least_squares(ode_model_resid, x0=theta_min, method = 'trf')
        theta_trf = results_trf.x

        random.seed(10)
        results_lm = least_squares(ode_model_resid, x0=theta_min, method = 'lm')
        theta_lm = results_lm.x

        x_y_sq = odeint(func=gLV_relative, y0=theta_sq[-(n_species + 1):], t=timepoints, args=(theta_sq,))
        x_y_trf = odeint(func=gLV_relative, y0=theta_trf[-(n_species + 1):], t=timepoints, args=(theta_trf,))
        x_y_lm = odeint(func=gLV_relative, y0=theta_lm[-(n_species+1):], t=timepoints, args=(theta_lm,))
        distance_sq = rmse(real_value, x_y_sq[:, :-1])
        distance_lm = rmse(real_value, x_y_lm[:, :-1])
        distance_trf = rmse(real_value, x_y_trf[:, :-1])

        if distance_sq < min_distance:
            min_distance = distance_sq
            min_theta = theta_sq
            method_used = "sq"
            x_y = x_y_sq

        if distance_trf < min_distance:
            min_distance = distance_trf
            min_theta = theta_trf
            method_used = "trf"
            x_y = x_y_trf

        if distance_lm < min_distance:
            min_distance = distance_lm
            min_theta = theta_lm
            method_used = "lm"
            x_y = x_y_lm

        end_time = tm.time()
        print(f"Run time: {end_time - start_time:.8f} seconds")

    fig1 = plot(x_y[:, :-1], real_value, timepoints)
    fig1.savefig(f"{output_dir}/abundance_over_time_{min_distance:.2f}_{method_used}.svg")

    tpoints = np.arange(timepoints[0], timepoints[-1]+timepoints[-1] / 180, timepoints[-1] / 180)
    predicted_relative_abundance = odeint(func=gLV_relative, y0=theta[-(n_species+1):], t=tpoints, args=(theta,))
    fig2 = plot_plate(predicted_relative_abundance[minutes, :-1])
    fig2.savefig(f"{output_dir}/plate_{minutes}.svg")

    return


def linear_regression(data, n_tpoints, time_seg, n_species):

    # ∆ (lnNi) / ∆ t = (1/ ∆t) * lnNi(tk+1) – (1/ ∆t) * lnNi(tk)
    for i in range(n_tpoints - 1):
        data.loc[n_tpoints + i] = (1 / time_seg) * np.log(data.loc[i + 1]) - (1 / time_seg) * np.log(data.loc[i])
    # (n_tpoints * 2 - 1 x n_species * 2)

    # Initialize empty vector for parameter estimates
    r_ini = np.zeros(n_species) # Intercept
    b_ini = np.zeros((n_species, n_species - 1)) # Slopes for linear regression

    # ∆ (lnNi) / ∆ t ~ d (lNi) / dt = dNi / dt / Ni = ri + sum(bijNj)
    for i in range(n_species):
        indep = data.columns[i+n_species] # Using absolute abundance estimates
        depen = [j for j in data.columns[n_species:] if j != indep]
        x = pd.DataFrame(data.loc[0:n_tpoints - 2, depen]) # Nj, Independent variables
        y = pd.DataFrame(data.loc[n_tpoints:2 * n_tpoints - 2, indep]) # ∆ (lnNi) / ∆ t, Dependent variable

        regr = linear_model.LinearRegression()
        regr.fit(x, y)
        r_ini[i] = regr.intercept_[0]
        b_ini[i, :] = regr.coef_[0, :]

    return np.concatenate((r_ini, b_ini.reshape(-1)))


@njit
def gLV_relative(X, t, theta):
        """
        # Todo: Modify for different n_species
        :param X: array of the observed relative abundances at time point 0 and the n0_est as last element
        :param theta: array of the estimated parameters
        :param t: array of the time points
        :return: gLV model defined with relative abundances and inter-species sum of abundances
        """
        x, y, z, v, w, n = X
        r1, r2, r3, r4, r5, b12, b13, b14, b15, b21, b23, b24, b25, b31, b32, b34, b35, b41, b42, b43, b45, b51, b52, b53, b54, x0, y0, z0, v0, w0, n0 = theta
        # equations
        dn_dt = r1 * x * n + b12 * x * y * n * n + b13 * x * z * n * n + b14 * x * v * n * n + b15 * x * w * n * n + r2 * y * n + b21 * x * y * n * n + b23 * y * z * n * n + b24 * y * v * n * n + b25 * y * w * n * n + r3 * z * n + b31 * x * z * n * n + b32 * y * z * n * n + b34 * z * v * n * n + b35 * z * w * n * n + r4 * v * n + b41 * v * x * n * n + b42 * v * y * n * n + b43 * v * z * n * n + b45 * v * w * n * n + r5 * w * n + b51 * w * x * n * n + b52 * w * y * n * n + b53 * w * z * n * n + b54 * w * v * n * n
        dx_dt = (r1 * x * n + b12 * x * y * n * n + b13 * x * z * n * n + b14 * x * v * n * n + b15 * x * w * n * n - x * dn_dt) / n
        dy_dt = (r2 * y * n + b21 * x * y * n * n + b23 * y * z * n * n + b24 * y * v * n * n + b25 * y * w * n * n - y * dn_dt) / n
        dz_dt = (r3 * z * n + b31 * x * z * n * n + b32 * y * z * n * n + b34 * z * v * n * n + b35 * z * w * n * n - z * dn_dt) / n
        dv_dt = (r4 * v * n + b41 * v * x * n * n + b42 * v * y * n * n + b43 * v * z * n * n + b45 * v * w * n * n - v * dn_dt) / n
        dw_dt = (r5 * w * n + b51 * w * x * n * n + b52 * w * y * n * n + b53 * w * z * n * n + b54 * w * v * n * n - w * dn_dt) / n
        return [dx_dt, dy_dt, dz_dt, dv_dt, dw_dt, dn_dt]

if __name__ == "__main__":
    import sys
    relative_abundance = str(sys.argv[1])
    minutes = int(sys.argv[2])
    num_run = int(sys.argv[3])
    n0_est = float(sys.argv[4])
    num_iteration = int(sys.argv[5])
    output_dir = str(sys.argv[6])
    if len(sys.argv) > 7:
        absolute_abundance = sys.argv[7]
    else:
        absolute_abundance = None
    iLV(relative_abundance, minutes, num_run, n0_est, num_iteration, output_dir, absolute_abundance)