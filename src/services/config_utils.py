import json
from flask import session

from services import utils as us


def create_config_structure(data: dict) -> dict:
    """
    Creates a configuration structure from the provided data.
    Args:
        data (dict): The data containing directory and metric information.
    Returns:
        dict: A dictionary with the configuration structure.
    """
    new_config_data = {"directories": {}, "metrics": {}, "graph-config": {}}
    directories = data.get("directory-list", [])
    labels = data.get("labels", [])
    for dir, label in zip(directories, labels):
        new_config_data["directories"][dir] = label

    grouped_metrics = session.get("grouped_metrics", {})
    metric_list_form = data.get("metric-list", [])
    for metric_group, metric_list in grouped_metrics.items():
        for metric in metric_list_form:
            if metric in metric_list:
                new_config_data["metrics"][metric_group] = new_config_data[
                    "metrics"
                ].get(metric_group, []) + [metric]

    graph_config = data.get("graph-config", {})
    new_config_data["graph-config"] = graph_config

    return new_config_data


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
                raise us.ExtractionError(
                    f"The configuration file '{path}' is not a valid JSON object."
                )
            if "directories" not in result or "metrics" not in result:
                raise us.ExtractionError(
                    f"The configuration file '{path}' must contain 'directories' and 'metrics' keys."
                )
            return result
    except FileNotFoundError as e:
        raise FileNotFoundError(f"The configuration file '{path}' does not exist.")
    except json.JSONDecodeError as e:
        raise us.ExtractionError(
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
