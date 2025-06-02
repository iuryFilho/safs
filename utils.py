import json


def to_json(obj):
    return json.dumps(obj, indent=4)


class Logger:
    def __init__(self, log=True, location=""):
        """
        Initializes the Logger instance.
        Args:
            log (bool): Whether to enable logging. Defaults to True.
            location (str): The location of the logger object.
        """
        self.log_enable = log
        self.location = location

    def log(self, message, enable=True):
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
