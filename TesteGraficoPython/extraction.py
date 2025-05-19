import glob
import os
import pandas as pd
import json


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


# def extract_labels_from_paths(paths: list[str]) -> list[str]:
#     """
#     Extracts the labels from the file paths.
#     Args:
#         paths (list[str]): List of file paths.
#     Returns:
#         list: A list of labels extracted from the file paths.
#     """

#     solutions = [s.split("/")[-2] for s in paths]
#     return [s.split("_", 1)[0] for s in solutions]


def load_simulation_results(paths: list[str]) -> list[pd.DataFrame]:
    """
    Loads the simulation results from the given file paths.
    Args:
        paths (list[str]): List of file paths to the simulation results.
    Returns:
        list: A list of DataFrames containing the simulation results.
    """

    return [pd.read_csv(s) for s in paths]


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


def get_paths_by_metric(base_directory: str, metric: str) -> list[str]:
    """
    Retrieves the csv file paths from the base directory based on the given metric.
    Args:
        base_directory (str): The base directory to search for files.
        metric (str): The file name pattern to search for.
    Returns:
        list: A list of csv file paths matching the given pattern.
    Raises:
        FileNotFoundError: If the base directory does not exist.
    """

    if not os.path.exists(base_directory):
        raise FileNotFoundError(
            f"The base directory '{base_directory}' does not exist."
        )
    pattern = base_directory + "/*/*" + metric
    file_paths = glob.glob(pattern)
    return [s.replace("\\", "/") for s in file_paths]


def get_csv_by_directory(simulation_directory: str) -> list[str]:
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
    pattern = simulation_directory + "/*.csv"
    file_paths = glob.glob(pattern)
    return [s.replace("\\", "/") for s in file_paths]


def extract_metric_group_names(file_paths: list[str]) -> list[str]:
    """
    Extracts the metric group names from the given file paths.
    Args:
        simulation_directory (str): The simulation directory to search for files.
    Returns:
        list: A list of metric group names found in the file paths.
    """
    file_names = [s.replace("\\", "/").split("/")[-1] for s in file_paths]
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
    pattern = base_directory + "/*/"
    paths = glob.glob(pattern)
    return [s.replace("\\", "/") for s in paths]


def group_metrics(
    metric_groups: list[str], file_paths: list[str]
) -> dict[str, list[str]]:
    """
    Groups the metrics by their names and file paths.
    Args:
        metric_groups (list): A list of metric groups.
        file_paths (list): A list of file paths.
    Returns:
        dict: A dictionary with metric groups as keys and file paths as values.
    """

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


def save_config(config: dict, path: str) -> tuple[str, str]:
    """
    Saves the configuration to a JSON file.
    Args:
        config (dict): The configuration data to save.
        path (str): The path to save the configuration file.
    Returns:
        (str, error): A message indicating the result of the save operation and an error if the file could not be saved.
    """
    if not path:
        return "No path provided", None
    try:
        with open(path, "w") as config_file:
            json.dump(config, config_file, indent=4)
        return "Configuration saved successfully", None
    except IOError:
        return "Failed to save configuration", f"Could not write to '{path}'"


if __name__ == "__main__":
    # Example usage
    base_directory = "TesteGraficoPython/simulations"
    simulation_directories, err = get_simulations_directories(base_directory)
    file_paths = get_csv_by_directory(simulation_directories[0])
    metric_groups = extract_metric_group_names(file_paths)
    grouped_metrics = group_metrics(metric_groups, file_paths)
    with open("result.json", "w") as result_file:
        result_file.write(json.dumps(grouped_metrics, indent=4))
