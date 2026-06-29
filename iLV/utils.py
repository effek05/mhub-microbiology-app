import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

from matplotlib.lines import Line2D

def convert_to_relative_abundance(absolute_csv, outputdir):
    """
    :param absolute_csv: csv file of absolute abundance
    :param outputdir
    :return: csv file of relative abundance
    """
    df = pd.read_csv(absolute_csv)

    for i in range(df.shape[0]):
        N_sum = sum(df.iloc[i,1:]) # Equation 2
        df.iloc[i,1:] = df.iloc[i,1:] / N_sum # Equation 3

    df.to_csv(outputdir, index=False)

    return df


def rmse(real_value, predicted_value):
    return np.sqrt(np.sum((np.array(np.array(real_value.iloc[:, :]) - predicted_value[:, :]))**2) / real_value.shape[0] / real_value.shape[1])

def plot(x_y, real_value, timepoints):
    fig, ax = plt.subplots()
    N = x_y.shape[1]
    colors = ["red", "blue", "green", "yellow", "black"]
    markers = Line2D.filled_markers[:N]
    for i in range(N):
        ax.plot(timepoints, x_y[:, i], color=colors[i], lw=1, alpha=0.5)
        ax.plot(timepoints, real_value.iloc[:, i], color=colors[i], marker=markers[i], linestyle="None")

    return fig

def plot_plate(predicted_relative_abundance):

    fig, ax = plt.subplots()
    colors = ["red", "blue", "green", "yellow", "black"]

    radius = 10
    center_x, center_y = 0, 0

    x = np.linspace(center_x - radius, center_x + radius, 500)
    y_upper = center_y + np.sqrt(radius ** 2 - (x - center_x) ** 2)
    y_lower = center_y - np.sqrt(radius ** 2 - (x - center_x) ** 2)

    ax.plot(x, y_upper, color='gold')
    ax.plot(x, y_lower, color='gold')
    ax.fill_between(x, y_lower, y_upper, color='skyblue', alpha=0.3)

    arbitrary_no = predicted_relative_abundance * 100

    for i in range(len(arbitrary_no)):
        x, y = generate_points_in_circle(math.ceil(arbitrary_no[i]), radius, (center_x, center_y))
        ax.scatter(x, y, color=colors[i], s = 3, marker="X")

    fig.gca().set_aspect('equal', adjustable='box')
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])

    for key, spine in ax.spines.items():
        spine.set_visible(False)

    return fig


def generate_points_in_circle(npoints, radius, center):

    xpoints = []
    ypoints = []

    while len(xpoints) < npoints:

        x = np.random.uniform(-radius, radius, npoints - len(xpoints))
        y = np.random.uniform(-radius, radius, npoints - len(xpoints))

        distance = np.sqrt(x ** 2 + y ** 2)

        mask = distance < radius

        xpoints.append(x[mask] + center[0])
        ypoints.append(y[mask] + center[1])

    return np.concatenate(xpoints), np.concatenate(ypoints)


