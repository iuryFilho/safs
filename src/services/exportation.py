import pandas as pd
import os.path as op

from data.metric_data import METRIC_GROUP_ALIASES
from services import path as ps, simulation as ss


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
        filename = ps.ensure_unique_filename(
            op.join(base_directory, metric_type), overwrite
        )
        self.set_full_dirs(base_directory, directories)
        self.labels = labels
        self.set_float_loads(loads)
        self.load_points = load_points
        self.set_int_load_points(load_points)
        self.fmt = TableFormatter(self.float_loads, self.int_load_points)
        with pd.ExcelWriter(f"{filename}.xlsx") as self.writer:
            for self.metric_group, self.metrics in chosen_grouped_metrics.items():
                self.set_simulation_results()
                self.set_tables_func()
                self.write_to_excel()

    def write_to_excel(self):
        metric_group_alias = METRIC_GROUP_ALIASES[self.metric_group]
        final_df = pd.concat(self.all_tables, ignore_index=True)
        final_df.to_excel(self.writer, sheet_name=metric_group_alias)

    def set_simulation_results(self):
        """
        Sets the simulation results based on the full directories and metric group.
        This method loads the simulation results from the specified directories
        and prepares them for graph generation.
        """
        self.simulation_results = ss.load_simulation_results(
            self.full_directories, self.metric_group
        )

    def set_table_format(self, metric_type: str):
        """
        Set the table format based on the type provided.
        Args:
            metric_type (str): The type of metric for which the table format is set.
        """
        set_tables_func = self.TABLE_FORMATS.get(metric_type, None)
        if set_tables_func is None:
            raise ValueError(f"Metric type not supported: {metric_type}")
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
        self.full_directories = ps.get_full_paths(base_directory, directories)

    def set_float_loads(self, loads: list[str]):
        """
        Converts the list of loads from strings to floats.
        Args:
            loads (list[str]): List of loads as strings.
        """
        self.float_loads = [float(load) for load in loads]

    def set_int_load_points(self, load_points: list[str]):
        """
        Converts the list of load points from strings to integers.
        Args:
            load_points (list[str]): List of load points as strings.
        """
        self.int_load_points = [int(lp) for lp in load_points]

    def set_tables_individual(self):
        """
        Sets the tables for metric of type 'individual'.
        """
        self.fmt.initialize_table_list(self.labels)
        for metric in self.metrics:
            results = ss.compile_data(
                self.simulation_results, [metric], "individual", self.load_points
            )

            self.fmt.set_table(results).add_table_title(
                "metric", metric
            ).append_table().append_empty_row()
        self.all_tables = self.fmt.tables

    def set_tables_grouped(self):
        """
        Sets the tables for metric of type 'grouped'.
        """
        self.fmt.initialize_table_list(self.metrics)
        for label, simulation_result in zip(self.labels, self.simulation_results):
            results = ss.compile_data(
                [simulation_result], self.metrics, "grouped", self.load_points
            )

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
