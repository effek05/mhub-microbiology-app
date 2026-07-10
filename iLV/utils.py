import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import networkx as nx

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
    # TODO: here to match ninas drawings but change later
    colors = ["#D65A0F", "#F59A23", "#95B681", "#0078F8", "#FF9000"]
    for i in range(N):
        ax.plot(timepoints, x_y[:, i], color=colors[i], lw=1, alpha=0.5)
        ax.plot(timepoints, real_value.iloc[:, i], color=colors[i], marker="X", linestyle="None")

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return fig

def plot_plate(predicted_relative_abundance):

    fig, ax = plt.subplots()
    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(1,1,1)
    colors = ["#D65A0F", "#F59A23", "#95B681", "#0078F8", "#FF9000"]

    radius = 10
    center_x, center_y = 0, 0

    x = np.linspace(center_x - radius, center_x + radius, 500)
    y_upper = center_y + np.sqrt(radius ** 2 - (x - center_x) ** 2)
    y_lower = center_y - np.sqrt(radius ** 2 - (x - center_x) ** 2)

    ax.plot(x, y_upper, color='gold')
    ax.plot(x, y_lower, color='gold')
    ax.fill_between(x, y_lower, y_upper, color='skyblue', alpha=0.3)

    arbitrary_no = predicted_relative_abundance * 100

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

    
    for i in range(len(arbitrary_no)):
        x, y = generate_points_in_circle(math.ceil(arbitrary_no[i]), radius, (center_x, center_y))
        ax.scatter(x, y, color=colors[i], s = 3, marker="X")

    fig.gca().set_aspect('equal', adjustable='box')
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])

    for key, spine in ax.spines.items():
        spine.set_visible(False)

    
    ax.set_aspect('equal', adjustable='box')

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

def rmse_over_iters(distance):
    fig, ax = plt.subplots()

    x = np.arange(0, len(distance), 1)

    ax.plot(x, distance, color = 'red', lw=1, alpha = 0.5)
    ax.set_xlabel("Iteration")
    ax.set_ylabel("RMSE")
    ax.set_ylim(0, np.max(distance) * 1.1)

    return fig

def interaction_network(betas, species_names):

    # b12, b13, b14, b15, b21, b23, b24, b25, b31, b32, b34, b35, b41, b42, b43, b45, b51, b52, b53, b54
    G = nx.Graph()

    # Todo: https://networkx.org/documentation/stable/auto_examples/drawing/plot_weighted_graph.html
    """
    - make thickness of edge prop to weight of interaction
    - make #FFD166 for inhibition and #1B98E0 for promotion
    - only plot edge if bigger than min by atleast 3 times 
    """
    count = 0
    betas = betas / sum(abs(betas))
    min_beta = min(abs(betas)) * 5
    for i in range(len(species_names)):
        for j in range(len(species_names)):
            if i != j:
                if abs(betas[count]) > min_beta:
                    G.add_edge(species_names[i], species_names[j], weight = betas[count])
                count += 1

    pos = nx.spring_layout(G, seed=7)

    nx.draw_networkx_nodes(G, pos, node_size=700)

    negative = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] < 0]
    positive = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 0]

    # edges
    nx.draw_networkx_edges(G, pos, edgelist=elarge, width=6, edge_color='')
    nx.draw_networkx_edges(
        G, pos, edgelist=esmall, width=6, alpha=0.5, edge_color="b", style="dashed"
    )

    # node labels
    nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")
    # edge weight labels
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, round(edge_labels, 2))

    plt.show()
    return



