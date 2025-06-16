import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from typing import Callable

from services import path_service as ps


matplotlib.use("agg")

markers = ["o", "v", "^", "s", "P", "x", "D", "_", "*", "2"]
linestyles = ["-", "--", "-.", ":", "-", "--", "-.", ":", "-", "--"]
hatches = ["", "/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"]


def plot_line_graph(
    dataframes: list[pd.DataFrame],
    loads: list[str],
    labels: list[str],
):
    """
    Plot a line graph with error bars.\\
    This function generates a line graph for the provided dataframes,
    loads, and labels, with error bars representing the uncertainty in the data.
    Args:
        dataframes (list[pd.DataFrame]): List of DataFrames containing the data to plot.
        loads (list[str]): List of loads for the x-axis.
        labels (list[str]): List of labels for the graph legend.
    """
    load_positions = list(range(len(loads)))
    for i in range(len(dataframes)):
        y = dataframes[i]["mean"]
        e = dataframes[i]["error"]
        plt.errorbar(
            load_positions,
            y,
            yerr=e,
            linestyle=linestyles[i % len(linestyles)],
            marker=markers[i % len(markers)],
            label=labels[i],
            fillstyle="none",
        )
    plt.xticks(load_positions, loads)


def plot_bar_graph(
    dataframes: list[pd.DataFrame],
    loads: list[str],
    labels: list[str],
):
    """
    Plot a bar graph with error bars.\\
    This function generates a bar graph for the provided dataframes,
    loads, and labels, with error bars representing the uncertainty in the data.
    Args:
        dataframes (list[pd.DataFrame]): List of DataFrames containing the data to plot.
        loads (list[str]): List of loads for the x-axis.
        labels (list[str]): List of labels for the graph legend.
    """
    bar_width = 0.15
    load_positions = list(range(len(loads)))
    for i in range(len(dataframes)):
        y = dataframes[i]["mean"]
        e = dataframes[i]["error"]
        plt.bar(
            [p + i * bar_width for p in load_positions],
            y,
            width=bar_width,
            label=labels[i],
            yerr=e,
            capsize=5,
            hatch=hatches[i % len(hatches)],
            edgecolor="black",
        )
        plt.xticks(
            [p + (len(dataframes) - 1) * bar_width / 2 for p in load_positions], loads
        )


def plot_stacked_bar_graph(
    dataframes: list[pd.DataFrame],
    loads: list[str],
    labels: list[str],
):
    """
    Plot a stacked bar graph with error bars.\\
    This function generates a stacked bar graph for the provided dataframes,
    loads, and labels, with error bars representing the uncertainty in the data.
    Args:
        dataframes (list[pd.DataFrame]): List of DataFrames containing the data to plot.
        loads (list[str]): List of loads for the x-axis.
        labels (list[str]): List of labels for the graph legend.
    """
    bar_width = 0.15
    load_positions = list(range(len(loads)))
    bottom = [0] * len(loads)
    for i in range(len(dataframes)):
        y = dataframes[i]["mean"]
        e = dataframes[i]["error"]
        plt.bar(
            load_positions,
            y,
            width=bar_width,
            label=labels[i],
            yerr=e,
            capsize=5,
            hatch=hatches[i % len(hatches)],
            edgecolor="black",
            bottom=bottom,
        )
        bottom = [b + y_val for b, y_val in zip(bottom, y)]
        plt.xticks(load_positions, loads)


plotting_strategies: dict[
    str, Callable[[list[pd.DataFrame], list[str], list[str]], None]
] = {
    "line": plot_line_graph,
    "bar": plot_bar_graph,
    "stacked-bar": plot_stacked_bar_graph,
}


def plot_graph(
    *,
    graph_type: str,
    dataframes: list[pd.DataFrame],
    loads: list[str],
    labels: list[str],
    x_label: str,
    y_label: str,
    fontsize: str,
    figsize: tuple[int, int],
    output_file: str,
    overwrite: bool,
    legend_position: str = "upper center",
    bbox_to_anchor: tuple[float, float] = (0.5, -0.15),
    max_columns: int = 5,
    frameon: bool = True,
):
    """
    Plot a graph based on the provided parameters.\\
    This function generates a graph using the specified type (line, bar, or stacked-bar)
    and saves it to the specified output file.
    Args:
        graph_type (str): Type of graph to generate (e.g., "line", "bar", "stacked-bar").
        dataframes (list[pd.DataFrame]): List of DataFrames containing the data to plot.
        loads (list[str]): List of loads for the x-axis.
        labels (list[str]): List of labels for the graph legend.
        x_label (str): Label for the x-axis.
        y_label (str): Label for the y-axis.
        fontsize (str): Font size for the labels.
        figsize (tuple[int, int]): Size of the figure for the graph.
        output_file (str): Path to save the output file (without extension).
        overwrite (bool): Whether to overwrite existing files.
        legend_position (str): Position of the legend in the graph.
        bbox_to_anchor (tuple[float, float]): Bounding box to anchor the legend.
        max_columns (int): Maximum number of columns in the legend.
        frameon (bool): Whether to draw a frame around the legend.
    """
    plt.figure(figsize=figsize)

    plot_function = plotting_strategies.get(graph_type)
    if plot_function is not None:
        plot_function(dataframes, loads, labels)
    else:
        raise ValueError(f"Graph type not supported: {graph_type}")

    plt.xlabel(x_label, fontsize=fontsize)
    plt.ylabel(y_label, fontsize=fontsize)
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    plt.grid(axis="y")
    if len(labels) < max_columns:
        max_columns = len(labels)

    plt.legend(
        loc=legend_position,
        bbox_to_anchor=bbox_to_anchor,
        ncol=max_columns,
        fontsize=fontsize,
        frameon=frameon,
    )
    if output_file != "":
        output_file = ps.ensure_unique_filename(output_file, overwrite)
        plt.savefig(f"{output_file}.png", dpi=150, bbox_inches="tight")
    plt.close()
