from typing import Callable, TypeAlias
import os.path as op

import pandas as pd
from data.metrics_data import METRIC_GROUP_ALIASES
from services import (
    metrics_utils as mus,
    path_utils as pus,
    plotting as ps,
    compilation as cs,
    simulation_utils as sus,
)

GroupedMetricT: TypeAlias = dict[str, list[str]]


class GraphGenerator:
    """
    Class to generate graphs based on simulation results and metrics.
    This class provides methods to generate individual or grouped graphs
    based on the provided parameters.
    """

    def __init__(
        self,
        base_directory: str,
        metric_type: str,
        language: str,
        graph_type: str,
        directories: list[str],
        dir_labels: list[str],
        grouped_metrics: GroupedMetricT,
        loads: list[str],
        load_points: list[str],
    ):
        self.GENERATION_STRATEGIES: dict[str, Callable] = {
            "individual": self.generate_individual,
            "grouped": self.generate_grouped,
        }
        self.graph_type = graph_type
        self.set_generation_strategy(metric_type)
        self.language = language
        if language == "pt":
            self.x_label = "Carga na rede (Erlangs)"
        elif language == "en":
            self.x_label = "Network Load (Erlangs)"
        else:
            raise ValueError(f"Idioma não suportado: {language}")
        self.set_filename_prefix(base_directory, graph_type)
        self.set_dir_labels(dir_labels, directories)
        self.set_full_dirs(base_directory, directories)
        self.grouped_metrics = grouped_metrics
        self.loads = loads
        self.load_points = load_points

        self.compiler = cs.DataCompiler(metric_type, load_points)

    def generate_graphs(
        self,
        ylim_low: str,
        ylim_up: str,
        x_axis_direction: str,
        title: str,
        xlabel: str,
        ylabel: str,
        graph_fontsize: int,
        legend_fontsize: int,
        figsize: list[float],
        overwrite: bool,
        use_grid: bool,
        anchor: list[float],
        legend_position: str,
        max_columns: int,
        frameon: bool,
    ):
        graph_config = {
            "ylim_low": ylim_low,
            "ylim_up": ylim_up,
            "x_axis_direction": x_axis_direction,
            "title": title,
            "xlabel": xlabel,
            "ylabel": ylabel,
            "graph_type": self.graph_type,
            "legend_fontsize": legend_fontsize,
            "graph_fontsize": graph_fontsize,
            "figsize": figsize,
            "overwrite": overwrite,
            "use_grid": use_grid,
            "bbox_to_anchor": anchor,
            "legend_position": legend_position,
            "max_columns": max_columns,
            "frameon": frameon,
        }
        self.plotter = ps.GraphPlotter(graph_config)

        for self.metric_group, metrics in self.grouped_metrics.items():
            try:
                self.metric_group_alias = METRIC_GROUP_ALIASES[self.metric_group]
            except KeyError:
                raise ValueError(f"Grupo de métrica desconhecido: {self.metric_group}")
            try:
                simulation_results = sus.load_simulation_results(
                    self.full_directories, self.metric_group
                )
            except Exception as e:
                raise ValueError(f"Erro ao carregar resultados de simulação:\n{e}")
            self.generation_func(metrics, simulation_results)
        return self

    def set_generation_strategy(self, metric_type: str):
        """
        Sets the generation strategy based on the metric type.
        Args:
            metric_type (str): The type of metric for which the generation strategy is set.
        Raises:
            ValueError: If the metric type is not supported.
        """
        generation_func = self.GENERATION_STRATEGIES.get(metric_type, None)
        if generation_func is None:
            raise ValueError(f"Tipo de métrica não suportado: {metric_type}")
        self.generation_func = generation_func

    def set_filename_prefix(self, base_directory: str, graph_type: str):
        """
        Sets the filename prefix for the graphs based on the base directory,
        graph type, and metric type.
        Args:
            base_directory (str): The base directory where the graphs will be saved.
            graph_type (str): The type of graph to be generated.
        """
        self.filename_prefix = op.join(base_directory, graph_type)

    def set_dir_labels(self, dir_labels: list[str], directories: list[str]):
        """
        Sets the directory labels for the graphs. If no labels are provided,
        it uses the directory names as labels.
        Args:
            dir_labels (list[str]): List of labels for the directories.
            directories (list[str]): List of directory names.
        """
        if not dir_labels:
            dir_labels = directories
        self.dir_labels = dir_labels

    def set_full_dirs(self, base_directory: str, directories: list[str]):
        """
        Sets the full directories for the graphs by joining the base directory
        with the provided directory names.
        Args:
            base_directory (str): The base directory where the data is stored
                and where the graphs will be saved.
            directories (list[str]): List of directory names.
        """
        self.full_directories = pus.get_full_paths(base_directory, directories)

    def generate_individual(
        self, metrics: list[str], simulation_results: list[pd.DataFrame]
    ):
        """
        Generates graphs for metrics of type 'individual'.\\
        This function compiles data for each individual metric and generates graphs
        based on the provided parameters.
        Args:
            metrics (list[str]): List of metrics to be plotted.
            simulation_results (list[pd.DataFrame]): List of DataFrames containing the simulation results.
        """
        self.compiler.set_simulation_results(simulation_results)
        try:
            self.plotter.initialize_graphs_data(
                self.loads,
                labels=self.dir_labels,
                x_label=self.x_label,
            )
        except Exception as e:
            raise Exception(f"Erro ao inicializar dados dos gráficos:\n{e}")
        for metric in metrics:
            self.compiler.set_metrics([metric])
            try:
                dataframes = self.compiler.compile_data()
            except Exception as e:
                raise Exception(
                    f"Erro ao compilar dados para a métrica '{metric}':\n{e}"
                )
            filename = (
                f"{self.filename_prefix}_{metric.replace(' ', '_').replace('/', '_')}"
            )
            try:
                y_label = mus.translate_metric(metric, self.language)
            except Exception as e:
                raise Exception(f"Erro ao traduzir métrica '{metric}':\n{e}")
            try:
                self.plotter.plot_graph(
                    dataframes,
                    output_file=filename,
                    y_label=y_label,
                )
            except Exception as e:
                raise Exception(
                    f"Erro ao plotar gráfico para a métrica '{metric}':\n{e}"
                )
        self.compiler.reset_data()

    def generate_grouped(
        self, metrics: list[str], simulation_results: list[pd.DataFrame]
    ):
        """
        Generates graphs for metrics of type 'grouped'.\\
        This function compiles data for each metric group and generates graphs
        based on the provided parameters.
        Args:
            metrics (list[str]): List of metrics to be plotted.
            simulation_results (list[pd.DataFrame]): List of DataFrames containing the simulation results.
        """
        self.compiler.set_metrics(metrics)
        y_label = mus.translate_metric(mus.get_metric_root(metrics[0]), self.language)
        translated_metrics = [
            mus.translate_metric(metric, self.language) for metric in metrics
        ]
        try:
            self.plotter.initialize_graphs_data(
                self.loads,
                labels=mus.get_metrics_components(translated_metrics, self.language),
                x_label=self.x_label,
                y_label=y_label,
            )
        except Exception as e:
            raise Exception(f"Erro ao inicializar dados dos gráficos:\n{e}")
        for label, simulation_result in zip(self.dir_labels, simulation_results):
            self.compiler.set_simulation_results([simulation_result])
            try:
                dataframes = self.compiler.compile_data()
            except Exception as e:
                raise Exception(
                    f"Erro ao compilar dados para o grupo '{self.metric_group}':\n{e}"
                )
            filename = f"{self.filename_prefix}_{self.metric_group_alias}_{label}"
            try:
                self.plotter.plot_graph(
                    dataframes,
                    output_file=filename,
                )
            except Exception as e:
                raise Exception(
                    f"Erro ao plotar gráfico para o grupo '{self.metric_group}':\n{e}"
                )
        self.compiler.reset_data()
