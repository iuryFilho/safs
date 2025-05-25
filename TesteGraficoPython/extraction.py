import glob
import os
import pandas as pd
import json
import logging


class ExtractionError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def filter_metric(
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
        if not os.path.exists(path):
            raise FileNotFoundError(f"The file '{path}' does not exist.")
        sep = "," if "," in open(path).readline() else ";"
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

    if not os.path.exists(path):
        raise FileNotFoundError(f"The file '{path}' does not exist.")
    with open(path, "r") as file:
        first_line = file.readline()
        sep = "," if "," in first_line else ";"
    df = pd.read_csv(path, sep=sep)
    return list(df["Metrics"].unique())


def get_csv_paths_by_metric(
    simulation_directories: list[str], metric: str
) -> list[str]:
    """
    Retrieves the csv file paths from the simulation directories based on the given metric.
    Args:
        simulation_directories (list[str]): The simulation directories to search for files.
        metric (str): The file name pattern to search for.
    Returns:
        list: A list of csv file paths matching the given pattern.
    Raises:
        FileNotFoundError: If any simulation directory does not exist.
    """
    file_paths = []
    for simulation_directory in simulation_directories:
        if not os.path.exists(simulation_directory):
            raise FileNotFoundError(
                f"The simulation directory '{simulation_directory}' does not exist."
            )
        pattern = f"{simulation_directory}/*_{metric}.csv"
        file_path = glob.glob(pattern)[0]
        file_paths.append(normalize_path(file_path))
    return file_paths


def normalize_path(s: str) -> str:
    return s.replace("\\", "/")


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
    if not os.path.exists(simulation_directory):
        raise FileNotFoundError(
            f"The simulation directory '{simulation_directory}' does not exist."
        )
    pattern = f"{simulation_directory}/*.csv"
    file_paths = glob.glob(pattern)
    return [normalize_path(s) for s in file_paths]


def extract_metric_group_names(file_paths: list[str]) -> list[str]:
    """
    Extracts the metric group names from the given file paths.
    Args:
        simulation_directory (str): The simulation directory to search for files.
    Returns:
        list: A list of metric group names found in the file paths.
    """
    file_names = [normalize_path(s).split("/")[-1] for s in file_paths]
    return [s.split("_")[-1].split(".")[0] for s in file_names]


def get_simulations_directories(base_directory: str) -> list[str]:
    """
    Retrieves the simulation directories from the base directory.
    Args:
        base_directory (str): The base directory to search for files.
    Returns:
        list: A list of simulation directories found in the directory.
    Raises:
        FileNotFoundError: If the base directory does not exist.
    """
    if not os.path.exists(base_directory):
        raise FileNotFoundError(
            f"The base directory '{base_directory}' does not exist."
        )
    pattern = f"{base_directory}/*/"
    paths = glob.glob(pattern)
    return [normalize_path(s) for s in paths]


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


def main():
    def to_json(obj):
        return json.dumps(obj, indent=4)

    # Example usage
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)
    base_directory = "TesteGraficoPython/simulations"
    logger.info(f"Base directory: {base_directory}")
    simulation_directories = get_simulations_directories(base_directory)
    logger.info(f"Simulation directories: {to_json(simulation_directories)}")
    simulation_directories_names = [s.split("/")[-2] for s in simulation_directories]
    logger.info(
        f"Simulation directories names: {to_json(simulation_directories_names)}"
    )
    csv_paths = get_csv_paths(simulation_directories[0])
    metric_groups = extract_metric_group_names(csv_paths)
    logger.info(f"Metric groups: {to_json(metric_groups)}")
    all_csv_paths_by_metric = {}
    for metric in metric_groups:
        all_csv_paths_by_metric[metric] = get_csv_paths_by_metric(
            simulation_directories, metric
        )
    logger.info(f"All csv paths by metric: {to_json(all_csv_paths_by_metric)}")
    # grouped_metrics = group_metrics(csv_paths)
    # logger.info(f"Grouped metrics: {to_json(grouped_metrics)}")


if __name__ == "__main__":
    main()
