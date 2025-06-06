import glob
import os.path as op
import os
import pandas as pd
import json
from control.utils import Logger


class ExtractionError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


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
        sep = get_separator(path)
        df = pd.read_csv(path, sep=sep)
        if "Metrics" not in df.columns:
            raise ExtractionError(
                f"The file '{path}' does not contain the 'Metrics' column."
            )
        dataframes.append(df)
    return dataframes


def get_metric_names(path: str) -> list[str]:
    """
    Retrieves the metric names from the given file path.
    Args:
        path (str): The file path to the simulation results.
    Returns:
        list: A list of metric names found in the file.
    Raises:
        FileNotFoundError: If the file does not exist.
    """

    if not op.exists(path):
        raise FileNotFoundError(f"The file '{path}' does not exist.")
    sep = get_separator(path)
    df = pd.read_csv(path, sep=sep)
    return list(df["Metrics"].unique())


def get_separator(path):
    with open(path, "r") as file:
        first_line = file.readline()
        sep = "," if "," in first_line else ";"
    return sep


def get_csv_paths_by_metric_group(
    simulation_directories: list[str], metric_group: str
) -> list[str]:
    """
    Retrieves the csv file paths from the simulation directories based on the given metric group.
    Args:
        simulation_directories (list[str]): The simulation directories to search for files.
        metric_group (str): The file name pattern to search for.
    Returns:
        list: A list of csv file paths matching the given pattern.
    Raises:
        FileNotFoundError: If any simulation directory does not exist.
    """
    file_paths = []
    for simulation_directory in simulation_directories:
        if not op.isdir(simulation_directory):
            raise FileNotFoundError(
                f"The simulation directory '{simulation_directory}' does not exist."
            )
        pattern = f"{simulation_directory}/*_{metric_group}.csv"
        file_path = glob.glob(pattern)[0]
        file_paths.append(op.normpath(file_path))
    return file_paths


def get_csv_paths(simulation_directory: str) -> list[str]:
    """
    Retrieves the csv file paths from the simulation directory.
    Args:
        simulation_directory (str): The simulation directory to search for files.
    Returns:
        list: A list of csv file paths found in the directory.
    Raises:
        FileNotFoundError: If the base directory does not exist.
    """
    if not op.isdir(simulation_directory):
        raise FileNotFoundError(
            f"The simulation directory '{simulation_directory}' does not exist."
        )
    pattern = f"{simulation_directory}/*.csv"
    file_paths = glob.glob(pattern)
    return [op.normpath(s) for s in file_paths]


def extract_metric_group_names(file_paths: list[str]) -> list[str]:
    """
    Extracts the metric group names from the given file paths.
    Args:
        simulation_directory (str): The simulation directory to search for files.
    Returns:
        list: A list of metric group names found in the file paths.
    """
    file_names = [get_basename(s) for s in file_paths]
    return [get_metric_suffix(s) for s in file_names]


def get_metric_suffix(filename):
    root: str = op.splitext(filename)[0]
    return root.split("_")[-1]


def get_simulations_directories(base_directory: str) -> list[str]:
    """
    Retrieves the simulation directories from the base directory.
    Args:
        base_directory (str): The base directory to search for directories.
    Returns:
        list: A list of simulation directories found in the directory.
    Raises:
        FileNotFoundError: If the base directory does not exist.
    """
    if not op.isdir(base_directory):
        raise FileNotFoundError(
            f"The base directory '{base_directory}' does not exist."
        )
    # List all entries and filter only directories
    entries = [op.join(base_directory, d) for d in os.listdir(base_directory)]
    dirs = [op.normpath(d) for d in entries if op.isdir(d)]
    return dirs


def group_metrics(file_paths: list[str]) -> dict[str, list[str]]:
    """
    Groups the metrics by their names and file paths.
    Args:
        metric_groups (list): A list of metric groups.
        file_paths (list): A list of file paths.
    Returns:
        dict: A dictionary with metric groups as keys and file paths as values.
    """
    metric_groups = extract_metric_group_names(file_paths)
    grouped_metrics = {}
    for metric_group, path in zip(metric_groups, file_paths):
        metrics = get_metric_names(path)
        grouped_metrics[metric_group] = metrics
    return grouped_metrics


def load_config(path: str) -> dict:
    """
    Loads the configuration from a JSON file.
    Args:
        path (str): The path to the configuration file.
    Returns:
        dict: A dictionary with the configuration data.
    Raises:
        FileNotFoundError: If the configuration file does not exist.
        ExtractionError: If the configuration file is not valid.
    """
    if not path:
        return {}
    try:
        with open(path, "r") as config_file:
            result = json.load(config_file)
            if not isinstance(result, dict):
                raise ExtractionError(
                    f"The configuration file '{path}' is not a valid JSON object."
                )
            if "directories" not in result or "metrics" not in result:
                raise ExtractionError(
                    f"The configuration file '{path}' must contain 'directories' and 'metrics' keys."
                )
            return result
    except FileNotFoundError as e:
        raise FileNotFoundError(f"The configuration file '{path}' does not exist.")
    except json.JSONDecodeError as e:
        raise ExtractionError(
            f"The configuration file '{path}' is not a valid JSON file."
        )


def save_config(config: dict, path: str) -> str:
    """
    Saves the configuration to a JSON file.
    Args:
        config (dict): The configuration data to save.
        path (str): The path to save the configuration file.
    Returns:
        str: A message indicating the result of the save operation.
    """
    if not path:
        return "No path provided"
    try:
        with open(path, "w") as config_file:
            json.dump(config, config_file, indent=4)
        return "Configuration saved successfully"
    except IOError:
        return "Failed to save configuration"


def extract_load_points(simulation_results: list[pd.DataFrame]) -> list[str]:
    """
    Extracts the load points from the simulation results.
    Args:
        simulation_results (list[DataFrame]): List of DataFrames containing the simulation results.
    Returns:
        list[str]: A list of load points extracted from the simulation results.
    """
    return simulation_results[0]["LoadPoint"].tolist()


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
    return len(extract_load_points(filtered_results))


def get_basename(path: str) -> str:
    return op.basename(op.normpath(path))


def main():
    def to_json(obj):
        return json.dumps(obj, indent=4)

    # Example usage
    logger = Logger(log=True)
    base_directory = "TesteGraficoPython/simulations"
    logger.log(f"Base directory: {base_directory}")
    simulation_directories = get_simulations_directories(base_directory)
    logger.log(f"Simulation directories: {to_json(simulation_directories)}")
    simulation_directories_names = [s.split("/")[-2] for s in simulation_directories]
    logger.log(f"Simulation directories names: {to_json(simulation_directories_names)}")
    csv_paths = get_csv_paths(simulation_directories[0])
    metric_groups = extract_metric_group_names(csv_paths)
    logger.log(f"Metric groups: {to_json(metric_groups)}")
    all_csv_paths_by_metric = {}
    for metric in metric_groups:
        all_csv_paths_by_metric[metric] = get_csv_paths_by_metric_group(
            simulation_directories, metric
        )
    logger.log(f"All csv paths by metric: {to_json(all_csv_paths_by_metric)}")
    # grouped_metrics = group_metrics(csv_paths)
    # logger.info(f"Grouped metrics: {to_json(grouped_metrics)}")


if __name__ == "__main__":
    main()
