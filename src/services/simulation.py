import os.path as op
import pandas as pd
from scipy import stats as st
from services import path as ps, utils as us


def compile_data(
    simulation_results: list[pd.DataFrame],
    metrics: list[str],
    metric_type: str,
    load_points: list[str],
) -> list[pd.DataFrame]:
    """
    Compiles data from simulation results based on the specified metrics and metric type.
    Args:
        simulation_results (list[pd.DataFrame]): The simulation results to compile.
        metrics (list[str]): The metrics to filter the results by.
        metric_type (str): The type of metrics, either "individual" or "grouped".
        load_points (list[str]): A list of load points to filter the results by. Defaults to None.
    Returns:
        list[pd.DataFrame]: A list of DataFrames containing the compiled data.
    """
    verified_type = verify_args_type(simulation_results, metrics, metric_type)
    if verified_type == "individual":
        length = len(simulation_results)
        metric_results = filter_result_list_by_metric(metrics[0], simulation_results)
    elif verified_type == "grouped":
        length = len(metrics)
        metric_results = filter_result_by_metric_list(metrics, simulation_results[0])
    else:
        raise ValueError(
            "Invalid arguments: 'simulation_results' must be a list of DataFrames "
            "and 'metrics' must be a string for individual metrics or a list of strings for grouped metrics."
        )

    if load_points is not None and len(load_points) > 0:
        load_points_set = {str(l) for l in load_points}
        for i in range(len(metric_results)):
            loadpoint_col = metric_results[i]["LoadPoint"]
            first = loadpoint_col.iloc[0]
            if isinstance(first, float) and first.is_integer():
                loadpoint_str = loadpoint_col.astype(int).astype(str)
            else:
                loadpoint_str = loadpoint_col.astype(str)
            metric_results[i] = metric_results[i][loadpoint_str.isin(load_points_set)]

    final_results = extract_repetitions(metric_results)
    del metric_results

    number_of_reps = get_number_of_repetitions(final_results)
    average = calculate_average(final_results)
    error = calculate_standard_error(final_results, number_of_reps)
    del final_results

    dataframes = [pd.DataFrame() for _ in range(length)]

    for i in range(length):
        dataframes[i]["mean"] = average[i]
        dataframes[i]["error"] = error[i]
    return dataframes


def calculate_standard_error(
    data_list: list[pd.DataFrame], number_of_reps: int
) -> list:
    """
    Calculates the standard error of the mean for each DataFrame in the data list.
    Args:
        data (list[DataFrame]): List of DataFrames containing the data.
        number_of_reps (int): The number of repetitions.
    Returns:
        list: A list of standard errors for each DataFrame.
    """
    return [st.sem(d, axis=1, ddof=number_of_reps - 1).tolist() for d in data_list]


def get_number_of_repetitions(results_data: list[pd.DataFrame]) -> int:
    """
    Returns the number of repetitions in the results data.
    Args:
        results_data (list[DataFrame]): List of DataFrames containing the results data.
    Returns:
        int: The number of repetitions.
    """
    return len(results_data[0].columns)


def calculate_average(results_data: list[pd.DataFrame]) -> list:
    """
    Calculates the average of the results data.
    Args:
        results_data (list[DataFrame]): List of DataFrames containing the results data.
    Returns:
        list: A list of averages for each DataFrame.
    """
    return [d.mean(axis=1).tolist() for d in results_data]


def load_simulation_results(
    directory_paths: list[str], metric_group: str
) -> list[pd.DataFrame]:
    """
    Loads simulation results from CSV files based on the specified metric group.
    Args:
        directory_paths (list[str]): List of directories containing the simulation results.
        metric_group (str): The metric group to filter the CSV files by.
    Returns:
        list[pd.DataFrame]: A list of DataFrames containing the simulation results for the specified metric group.
    """
    dataframes = []
    paths = ps.get_csv_paths_by_metric_group(directory_paths, metric_group)
    if not paths:
        raise us.ExtractionError(
            f"No CSV files found for the metric group '{metric_group}'."
        )
    for path in paths:
        if not op.exists(path):
            raise FileNotFoundError(f"The file '{path}' does not exist.")
        sep = us.get_separator(path)
        df = pd.read_csv(path, sep=sep)
        if "Metrics" not in df.columns:
            raise us.ExtractionError(
                f"The file '{path}' does not contain the 'Metrics' column."
            )
        dataframes.append(df)
    return dataframes


def filter_result_list_by_metric(
    metric: str, simulation_results: list[pd.DataFrame]
) -> list[pd.DataFrame]:
    """
    Extracts the filtered metrics from the simulation results files.
    Args:
        metric (str): The metric to filter by.
        simulation_results (list[DataFrame]): List of DataFrames containing the simulation results.
    Returns:
        list: A list of DataFrames containing the filtered metrics.
    """
    return [d[d.Metrics == metric] for d in simulation_results]


def filter_result_by_metric_list(
    metrics: list[str], simulation_result: pd.DataFrame
) -> list[pd.DataFrame]:
    """
    Extracts the filtered metrics from the simulation result DataFrame.
    Args:
        metrics (list[str]): The metrics to filter by.
        simulation_result (DataFrame): The DataFrame containing the simulation results.
    Returns:
        list: A list of DataFrames containing the filtered metrics.
    """
    return [
        simulation_result[simulation_result.Metrics == metric] for metric in metrics
    ]


def extract_load_points(simulation_result: pd.DataFrame) -> list[str]:
    """
    Extracts the load points from the simulation result DataFrame.
    Args:
        simulation_result (DataFrame): DataFrame containing the simulation results.
    Returns:
        list[str]: A list of load points extracted from the simulation results.
    """
    return simulation_result["LoadPoint"].tolist()


def extract_repetitions(simulation_results: list[pd.DataFrame]) -> list:
    """
    Extracts the repetitions data from the simulation results.
    Args:
        simulation_results (list[DataFrame]): List of DataFrames containing the simulation results.
    Returns:
        list: A list of DataFrames containing the repetitions data.
    """

    return [d.filter(like="rep", axis=1) for d in simulation_results]


def get_load_count(directory_path: str, metric_group: str, metric: str) -> int:
    """
    Returns the number of load points for a given metric in a simulation results directory.
    Args:
        directory_path (str): The path to the directory containing the simulation results.
        metric_group (str): The metric group to filter the results by.
        metric (str): The specific metric to count load points for.
    Returns:
        int: The number of load points for the specified metric.
    """
    simulation_results = load_simulation_results([directory_path], metric_group)
    filtered_results = filter_result_list_by_metric(metric, simulation_results)
    return len(extract_load_points(filtered_results[0]))


def verify_args_type(
    simulation_results: list[pd.DataFrame],
    metrics: list[str],
    metric_type: str,
):
    """
    Checks the types of the arguments to determine if they match the expected types for individual or grouped metrics.
    Args:
        simulation_results (list[pd.DataFrame]): The simulation results to check.
        metrics (list[str]): The metrics to check.
        metric_type (str): The type of metrics, either "individual" or "grouped".
    Returns:
        str: Returns the metric type if it matches the expected types, otherwise returns an empty string.
    """
    if metric_type == "individual" and len(metrics) == 1:
        return "individual"
    if metric_type == "grouped" and len(simulation_results) == 1:
        return "grouped"
    return ""
