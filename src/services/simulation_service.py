import os.path as op
import pandas as pd
from scipy import stats as st
from services import utils_service as us, path_service as ps


def calculate_standard_error(repetitions_data, number_of_reps):
    return [
        st.sem(d, axis=1, ddof=number_of_reps - 1).tolist() for d in repetitions_data
    ]


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


def compile_individual_data(
    simulation_results: list[pd.DataFrame],
    metric: str,
    loads_filter: list = None,
) -> list[pd.DataFrame]:
    """
    Compiles the simulation results for the given metric and filters by load points if provided.
    Args:
        simulation_results (list[pd.DataFrame]): The list of simulations results to be compiled.
        metric (str): The specific metric to filter by.
        loads_filter (list, optional): List of load points to filter. Defaults to None.
    Returns:
        list: A list of DataFrames containing the compiled simulation results.
    """
    length = len(simulation_results)
    metric_results = filter_result_list_by_metric(metric, simulation_results)

    if loads_filter is not None and len(loads_filter) > 0:
        loads_filter_set = set(str(l) for l in loads_filter)
        for i in range(len(metric_results)):
            metric_results[i] = metric_results[i][
                metric_results[i]["LoadPoint"].astype(str).isin(loads_filter_set)
            ]

    loads = extract_load_points(metric_results[0])
    final_results = extract_repetitions(metric_results)
    del metric_results

    number_of_reps = get_number_of_repetitions(final_results)
    average = calculate_average(final_results)
    error = calculate_standard_error(final_results, number_of_reps)
    del final_results

    dataframes = [pd.DataFrame() for _ in range(length)]

    for i in range(length):
        dataframes[i]["loads"] = loads
        dataframes[i]["mean"] = average[i]
        dataframes[i]["error"] = error[i]
    return dataframes


def compile_grouped_data(
    simulation_result: pd.DataFrame,
    metrics: list[str],
    loads_filter: list = None,
) -> list[pd.DataFrame]:
    """
    Compiles the simulation results for the given metrics and filters by load points if provided.
    This function is used when multiple metrics are grouped together.
    Args:
        simulation_result (pd.DataFrame): The simulation result to be compiled.
        metrics (list[str]): The list of metrics to filter by.
        loads_filter (list, optional): List of load points to filter. Defaults to None.
    Returns:
        list: A list of DataFrames containing the compiled simulation results.
    """
    length = len(metrics)
    metric_results = filter_result_by_metric_list(metrics, simulation_result)

    if loads_filter is not None and len(loads_filter) > 0:
        loads_filter_set = set(str(l) for l in loads_filter)
        for i in range(len(metric_results)):
            metric_results[i] = metric_results[i][
                metric_results[i]["LoadPoint"].astype(str).isin(loads_filter_set)
            ]

    loads = extract_load_points(metric_results[0])
    final_results = extract_repetitions(metric_results)
    del metric_results

    number_of_reps = get_number_of_repetitions(final_results)
    average = calculate_average(final_results)
    error = calculate_standard_error(final_results, number_of_reps)
    del final_results

    dataframes = [pd.DataFrame() for _ in range(length)]

    for i in range(length):
        dataframes[i]["loads"] = loads
        dataframes[i]["mean"] = average[i]
        dataframes[i]["error"] = error[i]
    return dataframes


def main():
    return


if __name__ == "__main__":
    main()
