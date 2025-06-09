import pandas as pd
import os.path as op

from services import path_utils as pus, utils as us


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
    sep = us.get_separator(path)
    df = pd.read_csv(path, sep=sep)
    return list(df["Metrics"].unique())


def group_metrics(file_paths: list[str]) -> dict[str, list[str]]:
    """
    Groups the metrics by their file paths.
    Args:
        file_paths (list): A list of file paths.
    Returns:
        dict: A dictionary with metric group names as keys and lists of metrics as values.
    """
    metric_group_names = extract_metric_group_names(file_paths)
    grouped_metrics = {}
    for group_name, path in zip(metric_group_names, file_paths):
        metrics = get_metric_names(path)
        grouped_metrics[group_name] = metrics
    return grouped_metrics


def extract_metric_group_names(file_paths: list[str]) -> list[str]:
    """
    Extracts the metric group names from the given file paths.
    Args:
        simulation_directory (str): The simulation directory to search for files.
    Returns:
        list: A list of metric group names found in the file paths.
    """
    file_names = [pus.get_basename(s) for s in file_paths]
    return [get_metric_suffix(s) for s in file_names]


def filter_chosen_metrics(
    grouped_metrics: dict[str, list[str]], chosen_metrics: list[str]
) -> dict[str, list[str]]:
    """
    Filters the grouped metrics based on the chosen metrics.
    Args:
        grouped_metrics (dict[str, list[str]]): A dictionary with metric groups as keys and lists of metrics as values.
        chosen_metrics (list[str]): A list of chosen metrics to filter by.
    Returns:
        dict[str, list[str]]: A dictionary with metric groups as keys and lists of chosen metrics as values.
    """
    chosen_grouped_metrics = {}
    for group_name, metric_list in grouped_metrics.items():
        for metric in chosen_metrics:
            if metric in metric_list:
                chosen_grouped_metrics[group_name] = chosen_grouped_metrics.get(
                    group_name, []
                ) + [metric]

    return chosen_grouped_metrics


def get_metric_suffix(filename: str) -> str:
    """
    Extracts the metric suffix from the given filename.
    Args:
        filename (str): The filename to extract the metric suffix from.
    Returns:
        str: The metric suffix extracted from the filename.
    """
    root: str = op.splitext(filename)[0]
    return root.split("_")[-1]
