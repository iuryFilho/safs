import json


class ExtractionError(Exception):
    """
    Custom exception for errors during data extraction.
    """

    def __init__(self, message):
        """
        Initializes the ExtractionError instance.
        Args:
            message (str): The error message to be displayed.
        """
        super().__init__(message)
        self.message = message


class Logger:
    """
    A simple logger class for debugging purposes.
    This class can be used to enable or disable logging and set a location prefix.
    """

    def __init__(self, log=True, location=""):
        """
        Initializes the Logger instance.
        Args:
            log (bool): Whether to enable logging. Defaults to True.
            location (str): The location of the logger object.
        """
        self.log_enable = log
        self.location = location

    def debug(self, message, enable=True):
        """
        Logs a debug message.
        Args:
            message (str): The message to log.
        """
        if self.log_enable and enable:
            if self.location:
                print(f"DEBUG - {self.location}: {message}")
            else:
                print(f"DEBUG: {message}")


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
        *values (str): A variable number of string values to be converted to floats.
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


def extract_labels(directories, raw_labels):
    labels = []
    session_labels = {}
    for dir, label in zip(directories, raw_labels):
        if label:
            labels.append(label)
            session_labels[dir] = label
        else:
            labels.append(dir)
    return labels, session_labels
