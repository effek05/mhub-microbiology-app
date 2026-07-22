import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import networkx as nx
import matplotlib.patches
import matplotlib as mpl

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

def plot(x_y, real_value, timepoints, species_names, method_used, min_distance):
    fig, ax = plt.subplots()
    N = x_y.shape[1]

    cmap = mpl.colormaps['viridis']
    colors = cmap(np.linspace(0, 1, N))

    for i in range(N):
        ax.plot(timepoints, x_y[:, i], color=colors[i], lw=1, label = f"Estimated {species_names[i]}")
        ax.plot(timepoints, real_value.iloc[:, i], color=colors[i], marker="X", linestyle="None",  label = f"Observed {species_names[i]}")

    ax.set_ylabel("Relative Abundance")
    ax.set_xlabel("Time")
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.set_title(f"Method used: {method_used}, RMSE:{min_distance:.3f}")

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return fig

def plot_plate(predicted_relative_abundance):

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

    fig, ax = plt.subplots(figsize=(10, 10))
    G = nx.DiGraph()
    count = 0
    min_beta = min(abs(betas))
    if len(species_names) > 3:
        for i in range(len(species_names)):
            for j in range(len(species_names)):
                if i != j:
                    if abs(betas[count]) > min_beta * 5:
                        # Si
                        G.add_weighted_edges_from([(species_names[j], species_names[i], betas[count])])
                    count += 1
    else:
        for i in range(len(species_names)):
            for j in range(len(species_names)):
                if i != j:
                    G.add_weighted_edges_from([(species_names[j], species_names[i], betas[count])])
                    count += 1

    pos = nx.circular_layout(G)
    normalize_weight = 10 ** (len(str(int(max(abs(betas))))) - 1)
    nx.draw_networkx_nodes(G, pos, node_size=5000, node_color='#0B4F6C', ax = ax)

    negative = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] < 0]
    negative_weights = [d['weight'] / normalize_weight for (u, v, d) in G.edges(data=True) if d["weight"] < 0]
    positive = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 0]
    positive_weights = [d['weight'] / normalize_weight for (u, v, d) in G.edges(data=True) if d["weight"] > 0]

    testArrow = matplotlib.patches.ArrowStyle.Fancy(head_length=1, head_width=1.5, tail_width=.1)
    nx.draw_networkx_edges(G, pos, edgelist=negative, width = negative_weights, arrowsize= negative_weights,
                           node_size=7000, connectionstyle='arc3, rad = 0.1', arrowstyle=testArrow,
                           edge_color="red", ax = ax)
    nx.draw_networkx_edges(G, pos, edgelist=positive, width = positive_weights, arrowsize= positive_weights,
                           node_size=7000, connectionstyle='arc3, rad = 0.1', arrowstyle=testArrow,
                           edge_color="green", ax = ax)

    nx.draw_networkx_labels(G, pos, font_size=37, font_family="sans-serif", font_color="#F6F7EB", ax = ax)

    ax.axis('off')

    return fig

def foo(import_string):
    _globals = {}
    code = compile(import_string, '<string>', 'exec')
    exec(code, _globals)
    import sys
    g = globals()
    g.update(_globals)
    sys.modules.update(_globals)