import json

from services import utils as us, session_data_utils as sdus
from data.metric_data import FILTERED_METRICS as FM


def create_config_structure(data: sdus.Data) -> dict:
    """
    Creates a configuration structure from the provided data.
    Args:
        data (dict): The data containing directory and metric information.
    Returns:
        dict: A dictionary with the configuration structure.
    """
    new_config_data = {"directories": {}, "metrics": {}, "graph-config": {}}
    directories = data["directory-list"]
    labels = data["labels"]
    for dir, label in zip(directories, labels):
        new_config_data["directories"][dir] = label

    grouped_metrics = data["grouped-metrics"]
    new_config_data["metrics"] = grouped_metrics

    graph_config = data["graph-config"]
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
