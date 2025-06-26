from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Generic, TypeVar  # noqa: F401


class Authenticator(ABC):
    """
    Abstract base class for authenticators.

    This class defines the basic structure for any authenticator by requiring the implementation
    of a method to retrieve authentication headers, and provides a way to store and retrieve the host.
    """

    def __init__(self, host: str):
        """
        Initializes the Authenticator with the specified host.

        :param host: The base URL or endpoint for the service.
        """
        self.host = host

    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Retrieves the authentication headers to be sent with requests.

        Subclasses must override this method to return the appropriate headers.

        :return: A dictionary mapping header names to their values.
        """
        pass  # pragma: no cover

    def get_host(self) -> str:
        """
        Returns the stored host.

        :return: The host as a string.
        """
        return self.host


class Token:
    def __init__(self, access_token: str, expires_at: datetime):
        """
        Initializes a new Token instance.

        Parameters:
        - access_token (str): The JWT or OAuth token.
        - expires_at (datetime): The expiration time of the token. It should be timezone-aware.
          If a naive datetime is provided, it will be converted to an aware datetime in UTC.
        """
        self.access_token = access_token

        # Ensure expires_at is timezone-aware. If naive, assume UTC.
        if expires_at.tzinfo is None:
            self.expires_at = expires_at.replace(tzinfo=timezone.utc)
        else:
            self.expires_at = expires_at

    def is_expired(self) -> bool:
        """
        Checks if the token is expired by comparing the current UTC time
        with the token's expiration time.

        Returns:
        - bool: True if expired, False otherwise.
        """
        return datetime.now(timezone.utc) >= (self.expires_at - timedelta(minutes=5))
