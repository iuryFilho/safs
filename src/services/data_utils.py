from flask import session as flask_session, request
from typing import Any
from data.default_data import DEFAULT_SESSION as DS, DEFAULT_DATA as DD


class Session:
    """
    Custom session class to handle session data.
    """

    def __getitem__(self, key: str) -> Any:
        """
        Gets a value from the session.
        Args:
            key (str): The key to retrieve from the session.
        Returns:
            The value associated with the key in the session, the default value from DEFAULT_SESSION if the key is not found or None if the key is not in DEFAULT_SESSION.
        """
        return flask_session.get(key, DS.get(key, None))

    def update(self, data: dict[str, Any]):
        """
        Updates the session with the provided data.
        Args:
            data (dict[str, Any]): A dictionary containing the session data to update.
        """
        for key, value in data.items():
            flask_session[key] = value

    def clear_session(self) -> tuple[dict[str, str], int]:
        """Clears the session data."""
        try:
            flask_session.clear()
            return {"message": "Session cleared successfully."}, 200
        except Exception as e:
            return {"error": str(e)}, 500


session = Session()


class Data:
    """
    Custom Data class to handle request data.
    """

    def __init__(self):
        self.data: dict = request.get_json()

    def __getitem__(self, key: str) -> Any:
        """
        Gets a value from the Data dictionary.
        Args:
            key (str): The key to retrieve from the Data dictionary.
        Returns:
            The value associated with the key in the Data dictionary, the value from DEFAULT_DATA if the key is not found or None if the key is not in DEFAULT_DATA.
        """
        return self.data.get(key, DD.get(key, None))
