import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from typing import Callable

from services import path_utils as pus


matplotlib.use("agg")

MARKERS = ["o", "v", "^", "s", "P", "x", "D", "_", "*", "2"]
LINESTYLES = ["-", "--", "-.", ":", "-", "--", "-.", ":", "-", "--"]
HATCHES = ["", "/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"]


def plot_line_graph(
    dataframes: list[pd.DataFrame],
    loads: list[str],
    labels: list[str],
    colors: list,
):
    """
    Plot a line graph with error bars.\\
    This function generates a line graph for the provided dataframes,
    loads, and labels, with error bars representing the uncertainty in the data.
    Args:
        dataframes (list[pd.DataFrame]): List of DataFrames containing the data to plot.
        loads (list[str]): List of loads for the x-axis.
        labels (list[str]): List of labels for the graph legend.
        colors (list): List of colors to use for the lines and markers.
    """
    load_positions = list(range(len(loads)))
    colors_len = len(colors)
    capsize = 3
    idx_shift = 0
    idx_count = 0
    for i in range(len(dataframes)):
        if idx_count == colors_len:
            idx_count = 0
            idx_shift += 1
        style_idx = (i + idx_shift) % len(LINESTYLES)
        idx_count += 1
        mean = dataframes[i]["mean"]
        error = dataframes[i]["error"]
        if sum(mean == 0) >= 2:
            mean_len = len(mean)
            for idx in range(mean_len):
                if mean[idx] == 0 and idx < mean_len - 1 and mean[idx + 1] == 0:
                    continue
                if error[idx] > 0:
                    plt.errorbar(
                        [load_positions[idx]],
                        [mean[idx]],
                        yerr=[error[idx]],
                        capsize=capsize,
                        linestyle=LINESTYLES[style_idx],
                        marker=MARKERS[style_idx],
                        color=colors[i % colors_len],
                        elinewidth=1,
                        markerfacecolor="none",
                    )
                else:
                    plt.scatter(
                        load_positions[idx],
                        mean[idx],
                        marker=MARKERS[style_idx],
                        color=colors[i % colors_len],
                        facecolors="none",
                    )
        else:
            plt.errorbar(
                load_positions,
                mean,
                yerr=error,
                capsize=capsize,
                linestyle="none",
                marker=MARKERS[style_idx],
                color=colors[i % colors_len],
                elinewidth=1,
                markerfacecolor="none",
            )
        plt.plot(
            load_positions,
            mean,
            linestyle=LINESTYLES[style_idx],
            color=colors[i % colors_len],
        )
        plt.plot(
            [],
            [],
            linestyle=LINESTYLES[style_idx],
            marker=MARKERS[style_idx],
            color=colors[i % colors_len],
            markerfacecolor="none",
            label=labels[i],
        )
    plt.xticks(load_positions, loads)
    plt.ylim(bottom=0)


def plot_bar_graph(
    dataframes: list[pd.DataFrame],
    loads: list[str],
    labels: list[str],
    colors: list,
):
    """
    Plot a bar graph with error bars.\\
    This function generates a bar graph for the provided dataframes,
    loads, and labels, with error bars representing the uncertainty in the data.
    Args:
        dataframes (list[pd.DataFrame]): List of DataFrames containing the data to plot.
        loads (list[str]): List of loads for the x-axis.
        labels (list[str]): List of labels for the graph legend.
        colors (list): List of colors to use for the bars.
    """
    bar_width = 0.15
    load_positions = list(range(len(loads)))
    colors_len = len(colors)
    idx_shift = 0
    idx_count = 0
    for i in range(len(dataframes)):
        if idx_count == colors_len:
            idx_count = 0
            idx_shift += 1
        style_idx = (i + idx_shift) % len(HATCHES)
        idx_count += 1
        mean = dataframes[i]["mean"]
        error = dataframes[i]["error"]
        plt.bar(
            [p + i * bar_width for p in load_positions],
            mean,
            width=bar_width,
            label=labels[i],
            yerr=error,
            capsize=5,
            hatch=HATCHES[style_idx],
            color=colors[i % colors_len],
            edgecolor="black",
        )
    plt.xticks(
        [p + (len(dataframes) - 1) * bar_width / 2 for p in load_positions], loads
    )
    plt.ylim(bottom=0)


def plot_stacked_bar_graph(
    dataframes: list[pd.DataFrame],
    loads: list[str],
    labels: list[str],
    colors: list,
):
    """
    Plot a stacked bar graph with error bars.\\
    This function generates a stacked bar graph for the provided dataframes,
    loads, and labels, with error bars representing the uncertainty in the data.
    Args:
        dataframes (list[pd.DataFrame]): List of DataFrames containing the data to plot.
        loads (list[str]): List of loads for the x-axis.
        labels (list[str]): List of labels for the graph legend.
        colors (list): List of colors to use for the bars.
    """
    bar_width = 0.15
    load_positions = list(range(len(loads)))
    bottom = [0] * len(loads)
    colors_len = len(colors)
    idx_shift = 0
    idx_count = 0
    for i in range(len(dataframes)):
        if idx_count == colors_len:
            idx_count = 0
            idx_shift += 1
        style_idx = (i + idx_shift) % len(HATCHES)
        idx_count += 1
        y = dataframes[i]["mean"]
        e = dataframes[i]["error"]
        plt.bar(
            load_positions,
            y,
            width=bar_width,
            label=labels[i],
            yerr=e,
            capsize=5,
            hatch=HATCHES[style_idx],
            color=colors[i % colors_len],
            edgecolor="black",
            bottom=bottom,
        )
        bottom = [b + y_val for b, y_val in zip(bottom, y)]
    plt.xticks(load_positions, loads)
    plt.ylim(bottom=0)


PLOTTING_STRATEGIES: dict[
    str, Callable[[list[pd.DataFrame], list[str], list[str], list], None]
] = {
    "line": plot_line_graph,
    "bar": plot_bar_graph,
    "stacked": plot_stacked_bar_graph,
}


def plot_graph(
    *,
    graph_type: str,
    dataframes: list[pd.DataFrame],
    loads: list[str],
    labels: list[str],
    x_label: str,
    y_label: str,
    graph_fontsize: str,
    legend_fontsize: str,
    figsize: tuple[int, int],
    output_file: str,
    overwrite: bool,
    legend_position: str,
    bbox_to_anchor: tuple[float, float],
    max_columns: int,
    frameon: bool,
):
    """
    Plot a graph based on the provided parameters.\\
    This function generates a graph using the specified type (line, bar, or stacked)
    and saves it to the specified output file.
    Args:
        graph_type (str): Type of graph to generate (e.g., "line", "bar", "stacked").
        dataframes (list[pd.DataFrame]): List of DataFrames containing the data to plot.
        loads (list[str]): List of loads for the x-axis.
        labels (list[str]): List of labels for the graph legend.
        x_label (str): Label for the x-axis.
        y_label (str): Label for the y-axis.
        graph_fontsize (str): Font size for the graph text.
        legend_fontsize (str): Font size for the legend text.
        figsize (tuple[int, int]): Size of the figure for the graph.
        output_file (str): Path to save the output file (without extension).
        overwrite (bool): Whether to overwrite existing files.
        legend_position (str): Position of the legend in the graph.
        bbox_to_anchor (tuple[float, float]): Bounding box to anchor the legend.
        max_columns (int): Maximum number of columns in the legend.
        frameon (bool): Whether to draw a frame around the legend.
    """
    plt.figure(figsize=figsize)

    colors = get_colors(len(labels))

    plot_function = PLOTTING_STRATEGIES.get(graph_type)
    if plot_function is not None:
        plot_function(dataframes, loads, labels, colors)
    else:
        raise ValueError(f"Graph type not supported: {graph_type}")

    plt.xlabel(x_label, fontsize=graph_fontsize)
    plt.ylabel(y_label, fontsize=graph_fontsize)
    plt.xticks(fontsize=graph_fontsize)
    plt.yticks(fontsize=graph_fontsize)
    plt.grid(axis="y")
    if len(labels) < max_columns:
        max_columns = len(labels)

    if legend_position == "none":
        plt.legend().set_visible(False)
    else:
        plt.legend(
            loc=legend_position,
            bbox_to_anchor=bbox_to_anchor,
            ncol=max_columns,
            fontsize=legend_fontsize,
            frameon=frameon,
        )
    if output_file != "":
        output_file = pus.ensure_unique_filename(output_file, overwrite)
        plt.savefig(f"{output_file}.png", dpi=150, bbox_inches="tight")
    plt.close()


def get_colors(size: int) -> list:
    if size <= 0:
        raise ValueError("Size must be a positive integer.")
    if size <= 10:
        cmap = plt.get_cmap("tab10")
    else:
        cmap = plt.get_cmap("tab20")
    colors = [cmap(i) for i in range(cmap.N)]
    return colors
