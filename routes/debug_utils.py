import json


def to_json(obj):
    return json.dumps(obj, indent=4)


class Logger:
    def __init__(self, log=True):
        """
        Initializes the Logger instance.
        Args:
            log (bool): Whether to enable logging. Defaults to True.
        """
        self.LOG = log

    def log(self, message):
        """
        Logs a debug message.
        Args:
            message (str): The message to log.
        """
        if self.LOG:
            print(f"DEBUG: {message}")
