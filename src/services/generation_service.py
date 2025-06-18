from typing import Callable, TypeAlias
import pandas as pd
import os.path as op
from data.metric_data import METRIC_GROUP_ALIASES
from services import (
    metrics_service as ms,
    path_service as ps,
    plotting_service as pls,
    simulation_service as ss,
)

GroupedMetricT: TypeAlias = dict[str, list[str]]


def generate_individual_graphs(
    *,
    metrics: list[str],
    simulation_results: list[pd.DataFrame],
    dir_labels: list[str],
    loads: list[str],
    load_points: list[str],
    filename_prefix: str,
    **graph_kwargs: dict[str, any],
):
    """
    Generate graphs for individual metrics.\\
    This function compiles data for each individual metric and generates graphs
    based on the provided parameters.
    Args:
        metrics (list[str]): List of individual metrics to plot.
        simulation_results (list[pd.DataFrame]): List of DataFrames containing simulation results.
        dir_labels (list[str]): List of directory labels.
        loads (list[str]): List of loads for the x-axis.
        load_points (list[str]): List of load points for the x-axis.
        filename_prefix (str): Prefix for the output file names.
        graph_kwargs: Keyword arguments containing the following keys
            - **graph_type** (str): Type of graph to generate
                (e.g., "line", "bar", "stacked-bar").
            - **x_label** (str): Label for the x-axis.
            - **fontsize** (str): Font size for the labels.
            - **figsize** (tuple[int, int]): Size of the figure for the graph.
            - **overwrite** (bool): Whether to overwrite existing files.
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
        pls.plot_graph(
            dataframes=dataframes,
            loads=loads,
            labels=dir_labels,
            y_label=metric,
            output_file=filename,
            **graph_kwargs,
        )


def generate_grouped_graphs(
    *,
    metrics: list[str],
    metric_group: str,
    simulation_results: list[pd.DataFrame],
    dir_labels: list[str],
    loads: list[str],
    load_points: list[str],
    filename_prefix: str,
    **graph_kwargs: dict[str, any],
):
    """
    Generate graphs for grouped metrics.\\
    This function compiles data for each metric group and generates graphs
    based on the provided parameters.
    Args:
        metrics (list[str]): List of individual metrics to plot.
        metric_group (str): The metric group to which the metrics belong.
        simulation_results (list[pd.DataFrame]): List of DataFrames containing simulation results.
        dir_labels (list[str]): List of directory labels.
        loads (list[str]): List of loads for the x-axis.
        load_points (list[str]): List of load points for the x-axis.
        filename_prefix (str): Prefix for the output file names.
        graph_kwargs: Keyword arguments containing the following keys
            - **graph_type** (str): Type of graph to generate
                (e.g., "line", "bar", "stacked-bar").
            - **x_label** (str): Label for the x-axis.
            - **fontsize** (str): Font size for the labels.
            - **figsize** (tuple[int, int]): Size of the figure for the graph.
            - **overwrite** (bool): Whether to overwrite existing files.
    """
    for label, simulation_result in zip(dir_labels, simulation_results):
        dataframes = ss.compile_data(
            simulation_result,
            metrics,
            "grouped",
            load_points,
        )
        filename = f"{filename_prefix}_{metric_group}_{label}"
        pls.plot_graph(
            dataframes=dataframes,
            loads=loads,
            labels=ms.get_metrics_components(metrics),
            y_label=ms.get_metric_root(metrics[0]),
            output_file=filename,
            **graph_kwargs,
        )


GENERATION_STRATEGIES: dict[str, Callable] = {
    "individual": generate_individual_graphs,
    "grouped": generate_grouped_graphs,
}


def generate_graphs(
    *,
    base_directory: str,
    directories: list[str],
    grouped_metrics: GroupedMetricT,
    dir_labels: list[str],
    loads: list[str],
    load_points: list[str],
    fontsize: str,
    figsize: tuple[int, int],
    overwrite: bool,
    metric_type: str,
    graph_type: str,
):
    """
    Generate graphs based on the provided parameters.\\
    This function compiles data for individual or grouped metrics and generates
    graphs based on the specified graph type (line, bar, or stacked-bar).
    Args:
        base_directory (str): Base directory where the simulation results are stored.
        directories (list[str]): List of directories containing simulation results.
        grouped_metrics (GroupedMetricT): Dictionary containing grouped metrics.
        dir_labels (list[str]): List of directory labels for the graphs.
        loads (list[str]): List of loads for the x-axis.
        load_points (list[str]): List of load points for the x-axis.
        fontsize (str): Font size for the labels (default is "large").
        figsize (tuple[int, int]): Size of the figure for the graph (default is (10, 5)).
        overwrite (bool): Whether to overwrite existing files (default is True).
        metric_type (str): Type of metrics to generate graphs for
            ("individual" or "grouped", default is "individual").
        graph_type (str): Type of graph to generate
            ("line", "bar", or "stacked-bar", default is "line").
    """
    generate_function = GENERATION_STRATEGIES.get(metric_type)
    if generate_function is None:
        raise ValueError(f"Metric type not supported: {metric_type}")

    filename_prefix = op.join(
        base_directory, f"{ps.get_basename(base_directory)}_{graph_type}"
    )
    x_label = "Carga na rede (Erlangs)"
    if not dir_labels:
        dir_labels = directories
    full_directories = [op.join(base_directory, d) for d in directories]
    for metric_group, metrics in grouped_metrics.items():
        simulation_results = ss.load_simulation_results(full_directories, metric_group)
        metric_group_alias = METRIC_GROUP_ALIASES[metric_group]
        generate_function(
            metrics=metrics,
            metric_group=metric_group_alias,
            simulation_results=simulation_results,
            dir_labels=dir_labels,
            loads=loads,
            load_points=load_points,
            graph_type=graph_type,
            filename_prefix=filename_prefix,
            x_label=x_label,
            fontsize=fontsize,
            figsize=figsize,
            overwrite=overwrite,
        )
