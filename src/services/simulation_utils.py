import os.path as op
import pandas as pd
from scipy import stats as st
from services import path_utils as pus, utils as us


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
    paths = pus.get_csv_paths_by_metric_group(directory_paths, metric_group)
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
    filtered_results = []
    for sr in simulation_results:
        if "Metrics" not in sr.columns:
            raise us.ExtractionError(
                "The DataFrame does not contain the 'Metrics' column."
            )
        if metric not in sr["Metrics"].values:
            raise us.ExtractionError(
                f"The metric '{metric}' was not found in the DataFrame."
            )
        filtered_results.append(sr[sr.Metrics == metric])
    return filtered_results


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
    if "Metrics" not in simulation_result.columns:
        raise us.ExtractionError("The DataFrame does not contain the 'Metrics' column.")
    filtered_results = []
    for metric in metrics:
        if metric not in simulation_result["Metrics"].values:
            raise us.ExtractionError(
                f"The metric '{metric}' was not found in the DataFrame."
            )
        filtered_results.append(simulation_result[simulation_result.Metrics == metric])
    return filtered_results


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
