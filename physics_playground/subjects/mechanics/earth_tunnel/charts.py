"""Static analytical charts for Earth Tunnel."""

import matplotlib.pyplot as plt


def plot_figure(plot):
    fig, ax = plt.subplots()
    for s in plot.series:
        ax.plot(s.x, s.y, label=s.label)
    ax.set_xlabel(plot.x_label)
    ax.set_ylabel(plot.y_label)
    ax.set_title(plot.title)
    ax.grid(True)
    return fig
