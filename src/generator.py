import os.path as op
from typing import Callable

import pandas as pd
from services import (
    generation as gs,
    metrics as ms,
    plotting as pls,
    simulation as ss,
    utils as us,
)
from data.metric_data import METRIC_GROUP_ALIASES


class GraphGenerator:
    """
    Class to generate graphs based on simulation results and metrics.
    This class provides methods to generate individual or grouped graphs
    based on the provided parameters.
    """

    __GENERATION_STRATEGIES: dict[str, Callable] = {
        "individual": gs.generate_individual_graphs,
        "grouped": gs.generate_grouped_graphs,
    }

    __x_label = "Carga na rede (Erlangs)"

    def initialize_graphs_data(
        self,
        base_directory: str,
        metric_type: str,
        graph_type: str,
        dir_labels: list[str],
        directories: list[str],
        grouped_metrics: dict[str, dict[str, list[float]]],
        loads: list[str],
        load_points: list[str],
    ):
        self.base_directory = base_directory
        self.metric_type = metric_type
        self.graph_type = graph_type
        self.__set_generation_strategy(metric_type)
        self.__set_filename_prefix(
            base_directory,
            graph_type,
            metric_type,
        )
        self.__set_dir_labels(dir_labels, directories)
        self.__set_full_dirs(directories)
        self.grouped_metrics = grouped_metrics
        self.loads = loads
        self.load_points = load_points
        return self

    def generate_graphs(
        self,
        graph_fontsize,
        legend_fontsize,
        figsize,
        overwrite,
        bbox_to_anchor,
        legend_position,
        max_columns,
        frameon,
    ):
        for self.metric_group, self.metrics in self.grouped_metrics.items():
            self.__set_simulation_results()
            metric_group_alias = METRIC_GROUP_ALIASES[self.metric_group]
            self.generation_func(
                metric_group=metric_group_alias,
                simulation_results=self.simulation_results,
                dir_labels=self.dir_labels,
                loads=self.loads,
                load_points=self.load_points,
                graph_type=self.graph_type,
                filename_prefix=self.filename_prefix,
                x_label=self.__x_label,
                graph_fontsize=graph_fontsize,
                legend_fontsize=legend_fontsize,
                figsize=figsize,
                overwrite=overwrite,
                legend_position=legend_position,
                bbox_to_anchor=bbox_to_anchor,
                max_columns=max_columns,
                frameon=frameon,
            )

    def __set_simulation_results(self):
        self.simulation_results = ss.load_simulation_results(
            self.full_directories, self.metric_group
        )

    def __set_generation_strategy(self, metric_type: str):
        generation_func = self.__GENERATION_STRATEGIES.get(metric_type, None)
        if generation_func is None:
            raise ValueError(f"Metric type not supported: {metric_type}")
        self.generation_func = generation_func

    def __set_filename_prefix(
        self, base_directory: str, graph_type: str, metric_type: str
    ):
        self.filename_prefix = op.join(
            base_directory,
            us.capitalize_first_letters(graph_type, metric_type),
        )

    def __set_dir_labels(self, dir_labels: list[str], directories: list[str]):
        if not dir_labels:
            dir_labels = directories
        self.dir_labels = dir_labels

    def __set_full_dirs(self, directories: list[str]):
        self.full_directories = [
            op.join(self.base_directory, directory) for directory in directories
        ]

    def generate_individual(
        self,
        *,
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
                    (e.g., "line", "bar", "stacked").
                - **x_label** (str): Label for the x-axis.
                - **fontsize** (str): Font size for the labels.
                - **figsize** (tuple[int, int]): Size of the figure for the graph.
                - **overwrite** (bool): Whether to overwrite existing files.
        """
        graph_kwargs.pop("metric_group", None)
        for metric in self.metrics:
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

    def generate_grouped(
        self,
        *,
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
                    (e.g., "line", "bar", "stacked").
                - **x_label** (str): Label for the x-axis.
                - **fontsize** (str): Font size for the labels.
                - **figsize** (tuple[int, int]): Size of the figure for the graph.
                - **overwrite** (bool): Whether to overwrite existing files.
        """
        for label, simulation_result in zip(dir_labels, simulation_results):
            dataframes = ss.compile_data(
                simulation_result,
                self.metrics,
                "grouped",
                load_points,
            )
            filename = f"{filename_prefix}_{metric_group}_{label}"
            pls.plot_graph(
                dataframes=dataframes,
                loads=loads,
                labels=ms.get_metrics_components(self.metrics),
                y_label=ms.get_metric_root(self.metrics[0]),
                output_file=filename,
                **graph_kwargs,
            )


gg = GraphGenerator()
gg.initialize_graphs_data(
    base_directory=".",
    metric_type="individual",
    graph_type="line",
    dir_labels=["Label1", "Label2"],
    directories=["dir1", "dir2"],
    grouped_metrics={},
    loads=["load1", "load2"],
    load_points=["point1", "point2"],
    # graph_fontsize="12",
    # legend_fontsize="10",
    # figsize=(10, 5),
    # overwrite=True,
    # bbox_to_anchor=(0.5, 0.5),
    # legend_position="upper right",
    # max_columns=3,
    # frameon=True,
)
gg.generate_graphs(
    graph_fontsize="12",
    legend_fontsize="10",
    figsize=(10, 5),
    overwrite=True,
    bbox_to_anchor=(0.5, 0.5),
    legend_position="upper right",
    max_columns=3,
    frameon=True,
)
