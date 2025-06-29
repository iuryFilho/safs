import json

from services.data_utils import Data
from data.metrics_data import FILTERED_METRICS as FM


def create_config_structure(data: Data) -> dict:
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
                raise Exception(
                    f"O arquivo de configuração '{path}' não contém um objeto JSON válido."
                )
            return result
    except FileNotFoundError as e:
        raise FileNotFoundError(f"O arquivo de configuração '{path}' não existe.")
    except json.JSONDecodeError as e:
        raise Exception(
            f"O arquivo de configuração '{path}' não é um arquivo JSON válido."
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
        return "Configuração salva com sucesso"
    except IOError:
        return "Falha ao salvar a configuração"
