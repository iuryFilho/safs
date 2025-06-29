import pandas as pd
import os.path as op

from data.metrics_data import METRIC_GROUP_ALIASES
import os
from services import (
    compilation as cs,
    path_utils as pus,
    simulation_utils as sus,
)


class ResultExporter:
    def __init__(self):
        self.TABLE_FORMATS = {
            "individual": self.set_tables_individual,
            "grouped": self.set_tables_grouped,
        }

    def export_results(
        self,
        base_directory: str,
        metric_type: str,
        directories: list[str],
        labels: list[str],
        chosen_grouped_metrics: dict[str, list[str]],
        loads: list[str],
        load_points: list[str],
        overwrite: bool,
    ):
        self.set_table_format(metric_type)
        filename_prefix = op.join(base_directory, metric_type)
        filename = pus.ensure_unique_filename(filename_prefix, "xlsx", overwrite)
        self.set_full_dirs(base_directory, directories)
        float_loads = self.get_float_loads(loads)
        int_load_points = self.get_int_load_points(load_points)

        self.compiler = cs.DataCompiler(metric_type, load_points)
        self.fmt = TableFormatter(float_loads, int_load_points)
        previous_file_content = None
        if overwrite and op.exists(f"{filename}.xlsx"):
            try:
                previous_file_content = pd.read_excel(
                    f"{filename}.xlsx", sheet_name=None
                )
            except Exception as e:
                previous_file_content = None

        with pd.ExcelWriter(f"{filename}.xlsx") as self.writer:
            try:
                for metric_group, metrics in chosen_grouped_metrics.items():
                    try:
                        simulation_results = sus.load_simulation_results(
                            self.full_directories, metric_group
                        )
                    except Exception as e:
                        raise Exception(
                            f"Erro ao carregar resultados de simulação:\n{e}"
                        )
                    self.set_tables_func(metrics, simulation_results, labels)
                    try:
                        self.write_to_excel(metric_group)
                    except Exception as e:
                        raise Exception(
                            f"Erro ao escrever resultados de simulação para o grupo '{metric_group}':\n{e}"
                        )
            except Exception as e:
                if previous_file_content is not None:
                    for sheet_name, df in previous_file_content.items():
                        df.to_excel(self.writer, sheet_name=sheet_name)
                else:
                    empty_df = pd.DataFrame()
                    empty_df.to_excel(self.writer)
                raise e

    def write_to_excel(self, metric_group: str):
        metric_group_alias = METRIC_GROUP_ALIASES[metric_group]
        final_df = pd.concat(self.all_tables, ignore_index=True)
        final_df.to_excel(self.writer, sheet_name=metric_group_alias)

    def set_table_format(self, metric_type: str):
        """
        Set the table format based on the type provided.
        Args:
            metric_type (str): The type of metric for which the table format is set.
        """
        set_tables_func = self.TABLE_FORMATS.get(metric_type, None)
        if set_tables_func is None:
            raise ValueError(f"Tipo de métrica não suportado: {metric_type}")
        self.set_tables_func = set_tables_func

    def set_full_dirs(self, base_directory: str, directories: list[str]):
        """
        Sets the full directories for the exportation by joining the base directory
        with the provided directory names.
        Args:
            base_directory (str): The base directory where the data is stored
                and where the results will be saved.
            directories (list[str]): List of directory names.
        """
        self.full_directories = pus.get_full_paths(base_directory, directories)

    def get_float_loads(self, loads: list[str]) -> list[float]:
        """
        Converts the list of loads from strings to floats.
        Args:
            loads (list[str]): List of loads as strings.
        Returns:
            list[float]: List of loads as floats.
        """
        return [float(load) for load in loads]

    def get_int_load_points(self, load_points: list[str]) -> list[int]:
        """
        Converts the list of load points from strings to integers.
        Args:
            load_points (list[str]): List of load points as strings.
        Returns:
            list[int]: List of load points as integers.
        """
        return [int(lp) for lp in load_points]

    def set_tables_individual(
        self,
        metrics: list[str],
        simulation_results: list[pd.DataFrame],
        labels: list[str],
    ):
        """
        Sets the tables for metric of type 'individual'.
        Args:
            metrics (list[str]): List of metrics to be included in the tables.
            simulation_results (list[pd.DataFrame]): List of DataFrames containing simulation results.
            labels (list[str]): List of labels for the simulation results.
        """
        self.fmt.initialize_table_list(labels)
        self.compiler.set_simulation_results(simulation_results)
        for metric in metrics:
            self.compiler.set_metrics([metric])
            results = self.compiler.compile_data()

            self.fmt.set_table(results).add_table_title(
                "metric", metric
            ).append_table().append_empty_row()
        self.all_tables = self.fmt.tables

    def set_tables_grouped(
        self,
        metrics: list[str],
        simulation_results: list[pd.DataFrame],
        labels: list[str],
    ):
        """
        Sets the tables for metric of type 'grouped'.
        Args:
            metrics (list[str]): List of metrics to be included in the tables.
            simulation_results (list[pd.DataFrame]): List of DataFrames containing simulation results.
            labels (list[str]): List of labels for the simulation results.
        """
        self.fmt.initialize_table_list(metrics)
        self.compiler.set_metrics(metrics)
        for label, simulation_result in zip(labels, simulation_results):
            self.compiler.set_simulation_results([simulation_result])
            results = self.compiler.compile_data()

            self.fmt.set_table(results).add_table_title(
                "solution", label
            ).append_table().append_empty_row()
        self.all_tables = self.fmt.tables


class TableFormatter:
    def __init__(self, float_loads: list[float], int_load_points: list[int]):
        """
        Initializes the TableFormatter with the provided float loads and integer load points.
        """
        self.float_loads = float_loads
        self.int_load_points = int_load_points

    def initialize_table_list(self, headers: list[str]):
        """
        Initializes the list of tables to an empty list and sets the headers.
        Args:
            headers (list[str]): List of headers to be used in the tables.
        """
        self.tables = []
        self.headers = headers
        return self

    def append_table(self):
        """
        Appends the current table DataFrame to the list of tables.
        This method appends the current table DataFrame to the list of tables
        maintained by the TableFormatter instance.
        """
        self.tables.append(self.table)
        return self

    def set_table(self, results: list[pd.DataFrame]):
        """
        Sets the table DataFrame with the current data.\\
        This method constructs a DataFrame with the specified headers,
        integer load points, and float loads, and calculates the mean and error
        for each header in the results.
        Args:
            results (list[pd.DataFrame]): List of DataFrames containing results.
        """
        columns = [("", "point"), ("", "load")]
        data: list = [self.int_load_points, self.float_loads]
        for header, result in zip(self.headers, results):
            columns.append((header, "mean"))
            columns.append((header, "error"))
            data.append(result["mean"])
            data.append(result["error"])
        self.table = pd.DataFrame(dict(zip(columns, data)))
        self.table.columns = pd.MultiIndex.from_tuples(self.table.columns)  # type: ignore
        return self

    def add_table_title(self, column_name: str, title: str):
        """
        Adds a new column with a specified title
        to the beginning of the current table DataFrame.
        Args:
            column_name (str): The name of the new column to be added.
            title (str): The title to be set in the first row of the new column.
        """
        self.table[("", column_name)] = ""
        self.table.at[0, ("", column_name)] = title
        cols = [("", column_name)] + [
            col for col in self.table.columns if col != ("", column_name)
        ]
        self.table = self.table[cols]
        return self

    def append_empty_row(self):
        """
        Appends an empty row with the same columns as the current table
        to the list of tables.
        """
        empty_row = pd.DataFrame(
            [[""] * len(self.table.columns)], columns=self.table.columns
        )
        self.tables.append(empty_row)
        return self
