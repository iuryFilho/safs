import pandas as pd
import os.path as op

from data.metric_data import METRIC_GROUP_ALIASES
from services import simulation_service as ss, path_service as ps


def assemble_results_table(
    headers: list[str],
    int_loads: list[int],
    load_points: list[str],
    results: list[pd.DataFrame],
) -> dict:
    """
    Assemble a results table from the given headers, loads,
    load points, and results.
    Args:
        headers (list[str]): List of headers for the results.
        int_loads (list[int]): List of integer loads.
        load_points (list[str]): List of load points.
        results (list[pd.DataFrame]): List of DataFrames containing the results.
    Returns:
        dict: A dictionary with MultiIndex columns and corresponding data.
    """
    columns = [("", "point"), ("", "load")]
    data = [load_points, int_loads]
    for header, df in zip(headers, results):
        columns.append((header, "mean"))
        columns.append((header, "error"))
        data.append(df["mean"])
        data.append(df["error"])
    return dict(zip(columns, data))


def add_label_column(column_name: str, label: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a new column with a specified label
    to the beginning of a pandas DataFrame.
    Args:
        column_name (str): The name of the new column to be added.
        label (str): The label to be set in the first row of the new column.
        df (pd.DataFrame): The DataFrame to which the column will be added.
    Returns:
        pd.DataFrame: A new DataFrame with the added column as the first column,
            containing the label in its first row and empty strings elsewhere.
    """
    df[("", column_name)] = ""
    df.at[0, ("", column_name)] = label
    cols = [("", column_name)] + [col for col in df.columns if col != ("", column_name)]
    return df[cols]


def create_empty_row(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a new DataFrame with a single empty row,
    matching the columns of the input DataFrame.
    Args:
        df (pd.DataFrame): The input DataFrame whose columns will be used.
    Returns:
        pd.DataFrame: A DataFrame with one row
            containing empty strings for each column.
    """
    return pd.DataFrame([[""] * len(df.columns)], columns=df.columns)


def export_individual_results(
    metrics: list[str],
    simulation_results: list[pd.DataFrame],
    labels: list[str],
    int_loads: list[int],
    load_points: list[str],
    int_load_points: list[int],
) -> list[pd.DataFrame]:
    """
    Exports individual simulation results to a list of DataFrames.
    Args:
        metrics (list[str]): List of metrics to export.
        simulation_results (list[pd.DataFrame]): List of DataFrames
            containing simulation results.
        labels (list[str]): List of labels for the simulations.
        int_loads (list[int]): List of integer loads.
        load_points (list[str]): List of load points.
        int_load_points (list[int]): List of integer load points.
    Returns:
        list[pd.DataFrame]: A list of DataFrames, each containing
            the results for a specific metric.
    """
    all_tables = []
    for metric in metrics:
        results = ss.compile_data(simulation_results, metric, "individual", load_points)

        table = assemble_results_table(labels, int_loads, int_load_points, results)
        out_df = pd.DataFrame(table)
        out_df.columns = pd.MultiIndex.from_tuples(out_df.columns)

        out_df = add_label_column("metric", metric, out_df)
        all_tables.append(out_df)

        empty_row = create_empty_row(out_df)
        all_tables.append(empty_row)
    return all_tables


def export_grouped_results(
    metrics: list[str],
    simulation_results: list[pd.DataFrame],
    labels: list[str],
    int_loads: list[int],
    load_points: list[str],
    int_load_points: list[int],
) -> list[pd.DataFrame]:
    """
    Exports grouped simulation results to a list of DataFrames.
    Args:
        metrics (list[str]): List of metrics to export.
        simulation_results (list[pd.DataFrame]): List of DataFrames
            containing simulation results.
        labels (list[str]): List of labels for the simulations.
        int_loads (list[int]): List of integer loads.
        load_points (list[str]): List of load points.
        int_load_points (list[int]): List of integer load points.
    Returns:
        list[pd.DataFrame]: A list of DataFrames, each containing
            the results for a specific metric group.
    """
    all_tables = []
    for label, simulation_result in zip(labels, simulation_results):
        results = ss.compile_data(simulation_result, metrics, "grouped", load_points)

        table = assemble_results_table(metrics, int_loads, int_load_points, results)
        out_df = pd.DataFrame(table)
        out_df.columns = pd.MultiIndex.from_tuples(out_df.columns)

        out_df = add_label_column("solution", label, out_df)
        all_tables.append(out_df)

        empty_row = create_empty_row(out_df)
        all_tables.append(empty_row)
    return all_tables


EXPORTATION_STRATEGIES = {
    "individual": export_individual_results,
    "grouped": export_grouped_results,
}


def export_results(
    base_directory: str,
    metric_type: str,
    directories: list[str],
    labels: list[str],
    chosen_grouped_metrics: dict[str, list[str]],
    loads: list[str],
    load_points: list[str],
    overwrite: bool,
):
    """
    Exports simulation results to an Excel file.
    Args:
        base_directory (str): The base directory where the results will be saved.
        metric_type (str): The type of metrics to export, either "individual" or "grouped".
        directories (list[str]): List of directories containing simulation results.
        labels (list[str]): List of labels for the simulations.
        chosen_grouped_metrics (dict[str, list[str]]): Dictionary mapping metric groups to their metrics.
        loads (list[str]): List of loads to be used in the results.
        load_points (list[str]): List of load points to be used in the results.
        overwrite (bool): Whether to overwrite existing files.
    """
    export_func = EXPORTATION_STRATEGIES.get(metric_type)
    if export_func is None:
        raise ValueError(f"Metric type not supported: {metric_type}")
    filename = op.join(
        base_directory, f"{ps.get_basename(base_directory)}_{metric_type}"
    )
    filename = ps.ensure_unique_filename(filename, overwrite)
    full_directories = [op.join(base_directory, d) for d in directories]
    int_loads = [int(l) for l in loads]
    int_load_points = [int(lp) for lp in load_points]
    with pd.ExcelWriter(f"{filename}.xlsx") as writer:
        for metric_group, metrics in chosen_grouped_metrics.items():
            simulation_results = ss.load_simulation_results(
                full_directories, metric_group
            )
            all_tables = export_func(
                metrics,
                simulation_results,
                labels,
                int_loads,
                load_points,
                int_load_points,
            )
            metric_group_alias = METRIC_GROUP_ALIASES[metric_group]
            final_df = pd.concat(all_tables, ignore_index=True)
            final_df.to_excel(writer, sheet_name=metric_group_alias)
