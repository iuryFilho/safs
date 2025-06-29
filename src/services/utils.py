import json


def to_json(obj: dict) -> str:
    """
    Converts a dictionary to a JSON string with indentation.
    Args:
        obj (dict): The dictionary to convert to JSON.
    Returns:
        str: The JSON string representation of the dictionary.
    """
    return json.dumps(obj, indent=4)


def to_float(*values: str) -> list[float]:
    """
    Converts a string or list of strings to a list of floats.
    Args:
        values (str): A variable number of string values to be converted to floats.
    Returns:
        list[float]: The converted values.
    """
    float_values = []
    for value in values:
        if value.find(",") != -1:
            float_values.append(float(value.replace(",", ".")))
        else:
            float_values.append(float(value))
    return float_values


def get_separator(path: str) -> str:
    """
    Determines the separator used in a CSV file based on its first line.
    Args:
        path (str): The path to the CSV file.
    Returns:
        str: The separator used in the CSV file, either ',' or ';'.
    """
    with open(path, "r") as file:
        first_line = file.readline()
        sep = "," if "," in first_line else ";"
    return sep


def extract_labels(
    directories: list[str], raw_labels: list[str]
) -> tuple[list[str], dict[str, str]]:
    """
    Extracts labels for directories based on provided raw labels.
    Args:
        directories (list[str]): List of directory names.
        raw_labels (list[str]): List of raw labels corresponding to the directories.
    Returns:
        tuple[list[str],dict[str,str]]: A tuple containing
        - A list of processed labels.
        - A dictionary mapping directory names to their labels.
    """
    labels = []
    session_labels = {}
    for dir, label in zip(directories, raw_labels):
        if label:
            labels.append(label)
            session_labels[dir] = label
        else:
            labels.append(dir)
    return labels, session_labels


def get_prefix(graph_type: str, metric_type: str) -> str:
    graph_pre = graph_type.capitalize()[:2]
    metric_pre = metric_type.capitalize()[:2]
    return f"{graph_pre}_{metric_pre}"
