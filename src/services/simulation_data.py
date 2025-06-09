import os.path as op
import pandas as pd
from scipy import stats as st
from services import utils as us


def load_simulation_results(paths: list[str]) -> list[pd.DataFrame]:
    """
    Loads the simulation results from the given file paths.
    Args:
        paths (list[str]): List of file paths to the simulation results.
    Returns:
        list: A list of DataFrames containing the simulation results.
    """
    dataframes = []
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


def get_load_count(metric: str, csv_path: str) -> int:
    """
    Retrieves the number of load points from the CSV file based on the given metric.
    Args:
        metric (str): The metric to filter by.
        csv_path (str): The path to the CSV file to analyze.
    Returns:
        int: The number of load points found in the CSV file for the specified metric.
    Raises:
        FileNotFoundError: If the CSV file does not exist.
    """
    if not op.exists(csv_path):
        raise FileNotFoundError(f"The CSV file '{csv_path}' does not exist.")
    simulation_results = load_simulation_results([csv_path])
    filtered_results = filter_result_list_by_metric(metric, simulation_results)
    return len(extract_load_points(filtered_results[0]))


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


def main():
    return


if __name__ == "__main__":
    main()
