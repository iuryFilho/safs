from flask import session
from typing import Any
from data.session_data import DEFAULT_SESSION as DS, DEFAULT_DATA as DD


def clear_session() -> tuple[dict[str, str], int]:
    """Clears the session data."""
    try:
        session.clear()
        return {"message": "Session cleared successfully."}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def set_session_data(data: dict[str, Any]):
    """
    Sets session data.
    Args:
        data (dict[str, Any]): A dictionary containing the session data to set.
    """
    for key, value in data.items():
        session[key] = value


def get_session(key: str) -> Any:
    """
    Gets a value from the session.
    If the key does not exist in the session, it will return the default value from DEFAULT_SESSION.
    Args:
        key (str): The key to retrieve from the session.
    Returns:
        The value associated with the key in the session, the default value if the key is not found or None if the key is not in DEFAULT_SESSION.
    """
    return session.get(key, DS.get(key, None))


class Data(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, key: str) -> Any:
        """
        Gets a value from the Data dictionary.
        Args:
            key (str): The key to retrieve from the Data dictionary.
        Returns:
            The value associated with the key in the Data dictionary, the value from DEFAULT_DATA if the key is not found or None if the key is not in DEFAULT_DATA.
        """
        return super().get(key, DD.get(key, None))
