import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import os.path as op
from typing import TypeAlias

from data.metric_data import METRIC_GROUP_ALIASES
from services import (
    utils_service as us,
    metrics_service as ms,
    path_service as ps,
    simulation_service as ss,
)


GroupedMetricT: TypeAlias = dict[str, list[str]]

matplotlib.use("agg")

LOG_ENABLE = True
logger = us.Logger(LOG_ENABLE, __name__)

markers = ["o", "v", "^", "s", "P", "x", "D", "_", "*", "2"]
linestyles = ["-", "--", "-.", ":", "-", "--", "-.", ":", "-", "--"]
hatches = ["", "/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"]


def generate_graphs(
    base_directory: str,
    directories: list[str],
    grouped_metrics: GroupedMetricT,
    labels: list[str] = [],
    loads: list[str] = [],
    load_points: list[str] = [],
    fontsize: str = "large",
    figsize: tuple[int, int] = (10, 5),
    overwrite: bool = True,
    metric_type: str = "individual",
    graph_type: str = "line",
):
    """
    Generate graphs based on the provided parameters.\\
    This function compiles data for individual or grouped metrics and generates
    graphs based on the specified graph type (line, bar, or stacked-bar).
    Args:
        base_directory: Base directory where the simulation results are stored.
        directories: List of directories containing simulation results.
        grouped_metrics: Dictionary containing grouped metrics.
        labels: List of labels for the graphs (optional).
        loads: List of loads for the x-axis (optional).
        load_points: List of load points for the x-axis (optional).
        fontsize: Font size for the labels (default is "large").
        figsize: Size of the figure for the graph (default is (10, 5)).
        overwrite: Whether to overwrite existing files (default is True).
        metric_type: Type of metrics to generate graphs for
            ("individual" or "grouped", default is "individual").
        graph_type: Type of graph to generate
            ("line", "bar", or "stacked-bar", default is "line").
    """
    if metric_type == "individual":
        generate_graphs_func = generate_individual_graphs
    elif metric_type == "grouped":
        generate_graphs_func = generate_grouped_graphs
    filename_prefix = op.join(
        base_directory, f"{ps.get_basename(base_directory)}_{graph_type}"
    )
    x_label = "Carga na rede (Erlangs)"
    if not labels:
        labels = directories
    full_directories = [op.join(base_directory, d) for d in directories]
    for metric_group, metrics in grouped_metrics.items():
        simulation_results = ss.load_simulation_results(full_directories, metric_group)
        metric_group_alias = METRIC_GROUP_ALIASES[metric_group]
        generate_graphs_func(
            metrics=metrics,
            metric_group=metric_group_alias,
            simulation_results=simulation_results,
            labels=labels,
            loads=loads,
            load_points=load_points,
            graph_type=graph_type,
            filename_prefix=filename_prefix,
            x_label=x_label,
            fontsize=fontsize,
            figsize=figsize,
            overwrite=overwrite,
        )


def generate_individual_graphs(
    metrics: list[str],
    simulation_results: list[pd.DataFrame],
    labels: list[str],
    loads: list[str],
    load_points: list[str],
    filename_prefix: str = "",
    **graph_kwargs: dict[str, any],
):
    """
    Generate graphs for individual metrics.\\
    This function compiles data for each individual metric and generates graphs
    based on the provided parameters.
    Args:
        metrics: List of individual metrics to plot.
        simulation_results: List of DataFrames containing simulation results.
        labels: List of labels for the graphs.
        loads: List of loads for the x-axis.
        load_points: List of load points for the x-axis.
        filename_prefix: Prefix for the output file names.
        graph_kwargs: Keyword arguments containing the following keys
            - **graph_type**: Type of graph to generate
                (e.g., "line", "bar", "stacked-bar").
            - **x_label**: Label for the x-axis.
            - **fontsize**: Font size for the labels.
            - **figsize**: Size of the figure for the graph.
            - **overwrite**: Whether to overwrite existing files.
    """
    graph_kwargs.pop("metric_group", None)
    for metric in metrics:
        dataframes = ss.compile_data(
            simulation_results,
            metric,
            "individual",
            load_points,
        )
        filename = f"{filename_prefix}_{metric.replace(' ', '_')}"
        plot_graph(
            dataframes=dataframes,
            loads=loads,
            labels=labels,
            y_label=metric,
            output_file=filename,
            **graph_kwargs,
        )


def generate_grouped_graphs(
    metrics: list[str],
    metric_group: str,
    simulation_results: list[pd.DataFrame],
    labels: list[str],
    loads: list[str],
    load_points: list[str],
    filename_prefix: str = "",
    **graph_kwargs: dict[str, any],
):
    """
    Generate graphs for grouped metrics.\\
    This function compiles data for each metric group and generates graphs
    based on the provided parameters.
    Args:
        metrics: List of individual metrics to plot.
        metric_group: The metric group to which the metrics belong.
        simulation_results: List of DataFrames containing simulation results.
        labels: List of labels for the graphs.
        loads: List of loads for the x-axis.
        load_points: List of load points for the x-axis.
        filename_prefix: Prefix for the output file names.
        graph_kwargs: Keyword arguments containing the following keys
            - **graph_type**: Type of graph to generate
                (e.g., "line", "bar", "stacked-bar").
            - **x_label**: Label for the x-axis.
            - **fontsize**: Font size for the labels.
            - **figsize**: Size of the figure for the graph.
            - **overwrite**: Whether to overwrite existing files.
    """
    for label, simulation_result in zip(labels, simulation_results):
        dataframes = ss.compile_data(
            simulation_result,
            metrics,
            "grouped",
            load_points,
        )
        filename = f"{filename_prefix}_{metric_group}_{label}"
        plot_graph(
            dataframes=dataframes,
            loads=loads,
            labels=ms.get_metrics_components(metrics),
            y_label=ms.get_metric_root(metrics[0]),
            output_file=filename,
            **graph_kwargs,
        )


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
        graph_type: Type of graph to generate (e.g., "line", "bar", "stacked-bar").
        dataframes: List of DataFrames containing the data to plot.
        loads: List of loads for the x-axis.
        labels: List of labels for the graph legend.
        x_label: Label for the x-axis.
        y_label: Label for the y-axis.
        fontsize: Font size for the labels.
        figsize: Size of the figure for the graph.
        output_file: Path to save the output file (without extension).
        overwrite: Whether to overwrite existing files.
        legend_position: Position of the legend in the graph.
        bbox_to_anchor: Bounding box to anchor the legend.
        max_columns: Maximum number of columns in the legend.
        frameon: Whether to draw a frame around the legend.
    """
    plt.figure(figsize=figsize)

    if graph_type == "line":
        plot_line_graph(dataframes, loads, labels)
    elif graph_type == "bar":
        plot_bar_graph(dataframes, loads, labels)
    elif graph_type == "stacked-bar":
        plot_stacked_bar_graph(dataframes, loads, labels)

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


def main():
    return


if __name__ == "__main__":
    main()
