import os
import time as tm
import numpy as np
import pandas as pd

from scipy.integrate import odeint
from scipy.optimize import least_squares
from sklearn import linear_model
from scipy.optimize import leastsq

from iLV.utils import convert_to_relative_abundance
from iLV.utils import rmse
from iLV.utils import plot
from iLV.utils import plot_plate
from iLV.utils import rmse_over_iters
from iLV.utils import interaction_network

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
    time_seg = 1
    n_species = df.shape[1] - 1

    working_dir = os.getcwd()
    if not os.path.exists(f"{working_dir}/iLV/gLV_relative_{n_species}.py"):
        write_gLV_file(working_dir, n_species)

    foo(f'from gLV_relative_{n_species} import gLV_relative')

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
        distance =  [None] * num_iteration
        distance_min = np.inf
        theta_min = theta_estimate

        for m in range(num_iteration):
            theta = theta_estimate
            x_y_hat = odeint(func=gLV_relative, y0=theta[-(n_species+1):], t=timepoints, args=(theta,), rtol=1e-8, atol=1e-10)

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
            return (np.abs(real_value - np.delete(odeint(func=gLV_relative, y0=theta[-(n_species + 1):], t=timepoints, args=(theta,), rtol=1e-8, atol=1e-10), -1, axis=1))
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

        x_y_sq = odeint(func=gLV_relative, y0=theta_sq[-(n_species + 1):], t=timepoints, args=(theta_sq,), rtol=1e-8, atol=1e-10)
        x_y_trf = odeint(func=gLV_relative, y0=theta_trf[-(n_species + 1):], t=timepoints, args=(theta_trf,), rtol=1e-8, atol=1e-10)
        x_y_lm = odeint(func=gLV_relative, y0=theta_lm[-(n_species+1):], t=timepoints, args=(theta_lm,), rtol=1e-8, atol=1e-10)
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
        run_time = end_time - start_time
        print(f"Run time: {run_time}")

    species_names = list(df.columns)[1:]

    if os.path.exists(f"{output_dir}_rmse_over_iters.svg") == False:
        fig1 = rmse_over_iters(distance)
        fig1.savefig(f"{output_dir}_rmse_over_iters.svg")

    if os.path.exists(f"{output_dir}/abundance_over_time_{min_distance:.2f}_{method_used}.png") == False:
        fig2 = plot(x_y[:, :-1], real_value, timepoints, species_names, method_used, min_distance)
        fig2.savefig(f"{output_dir}/abundance_over_time_{min_distance:.2f}_{method_used}.png")

    if os.path.exists(f"{output_dir}/plate_{minutes}.svg") == False:
        tpoints = np.arange(timepoints[0], timepoints[-1]+timepoints[-1] / 180, timepoints[-1] / 180)
        predicted_relative_abundance = odeint(func=gLV_relative, y0=theta[-(n_species+1):], t=tpoints, args=(theta,), rtol=1e-8, atol=1e-10)
        fig3 = plot_plate(predicted_relative_abundance[minutes, :-1])
        fig3.savefig(f"{output_dir}/plate_{minutes}.svg")

    if os.path.exists(f"{output_dir}/interaction_network_{min_distance:.2f}.png") == False:
        betas = min_theta[n_species:-(n_species + 1)]
        # Todo: Prob better if betas in matrix formulation
        fig4 = interaction_network(betas, species_names)
        fig4.savefig(f"{output_dir}/interaction_network_{min_distance:.2f}.png")

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

def foo(import_string):
    _globals = {}
    code = compile(import_string, '<string>', 'exec')
    exec(code, _globals)
    import sys
    g = globals()
    g.update(_globals)
    sys.modules.update(_globals)

def write_gLV_file(working_dir, n_species):
    """
    This writes a python script with gLV relative model for n_species

    :param working_dir: The directory where this new model will be stored
    :param n_species: Number of species

    The model made by this function has the following parameters:
        :param X: array of the observed relative abundances at time point 0 and the n0_est as last element
        :param theta: array of the estimated parameters
        :param t: array of the time points
        :return: gLV model defined with relative abundances and inter-species sum of abundances
    """

    with open(f"{working_dir}/iLV/gLV_relative_{n_species}.py", "w", encoding="utf-8") as f:
        f.write("from numba import njit\nimport warnings\nwarnings.filterwarnings('ignore')\n\n")
        f.write("@njit\ndef gLV_relative(X, t, theta):\n")

        growth_rates = ""
        X = ""
        absolute_equation = "\t\tdn_dt ="
        equations = ""
        interactions = ""
        initial_conditions = ""
        return_ = "\t\treturn ["
        for i in range(1, n_species + 1):
            if i == (n_species):
                initial_conditions += f"x{i}0"
            else:
                initial_conditions += f"x{i}0, "

            growth_rates += f"r{i}, "
            X += f"x{i}, "

            equations += f"\t\tdx{i}_dt = ((r{i} * x{i} * n)"
            return_ += f"dx{i}_dt, "
            if i != 1:
                absolute_equation += " +"
            absolute_equation += f" (r{i} * x{i} * n)"

            for j in range(1, n_species + 1):
                if i != j:
                    interactions += f"b{i}{j}, "
                    equations += f" + (b{i}{j} * x{i} * x{j} * n * n)"
                    absolute_equation += f" + (b{i}{j} * x{i} * x{j} * n * n)"
            equations += f" - (x{i} * dn_dt)) / n\n"

        X += "n"
        theta = growth_rates + interactions + initial_conditions
        return_ += "dn_dt]"

        f.write(f"\t\t{X} = X\n")
        f.write(f"\t\t{theta}, n0 = theta\n")
        f.write(f"{absolute_equation}\n")
        f.write(equations)
        f.write(return_)


    return

if __name__ == "__main__":
    import sys
    relative_abundance = str(sys.argv[1])
    minutes = int(sys.argv[2])
    num_run = int(sys.argv[3])
    n0_est = float(sys.argv[4])
    num_iteration = int(sys.argv[5])
    output_dir = str(sys.argv[6])
    # Optional argument for absolute abundance time series -> provide a file path for relative_abundance to
    # convert from absolute abundance to relative abundance
    if len(sys.argv) > 7:
        absolute_abundance = sys.argv[7]
    else:
        absolute_abundance = None
    iLV(relative_abundance, minutes, num_run, n0_est, num_iteration, output_dir, absolute_abundance)