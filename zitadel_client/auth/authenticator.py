from abc import ABC, abstractmethod


class Authenticator(ABC):
  """
  Abstract base class for authentication strategies.

  This class defines a common interface for implementing various
  authentication mechanisms. Subclasses must implement the
  `get_auth_headers` method to provide the necessary HTTP headers for
  authenticated API requests, as well as the `refresh_token` method for
  refreshing authentication tokens when needed.

  Attributes:
      host (str): The base URL for authentication endpoints.
  """

  def __init__(self, host: str):
    """
    Initialize the Authenticator with a host URL.

    Args:
        host (str): The base URL for all authentication endpoints.
    """
    self.host = host

  @abstractmethod
  def get_auth_headers(self) -> dict[str, str]:
    """
    Generate and return the authentication headers required for API requests.

    Subclasses must implement this method to return a dictionary where the keys
    are the header names and the values are the corresponding header values.

    Returns:
        dict[str, str]: A dictionary containing the authentication header(s).
    """
    pass

  @abstractmethod
  def refresh_token(self) -> None:
    """
    Refresh the authentication token.

    This abstract method must be implemented by subclasses that require a mechanism
    to refresh the authentication token. The implementation should update the token
    used by the authenticator.

    Returns:
        None
    """
    pass

  def get_host(self) -> str:
    """
    Retrieve the base host URL.

    This method returns the host URL that was specified during the instantiation
    of the Authenticator. It can be used by concrete classes or external consumers
    to build full endpoint URLs.

    Returns:
        str: The base URL for authentication endpoints.
    """
    return self.host
