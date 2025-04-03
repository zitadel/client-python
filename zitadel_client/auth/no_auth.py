from .authenticator import Authenticator


class DummyAuthenticator(Authenticator):
  """
  Authenticator implementation for testing purposes.

  This strategy does not apply any authentication to API requests.
  It is useful for testing environments where authentication is not required.
  """

  def __init__(self, host: str):
    """
    Initialize the DummyAuthenticator.

    Args:
        host (str): The base URL for all authentication endpoints.
    """
    super().__init__(host)

  def refresh_token(self) -> None:
    """
    Refresh the authentication token.

    For DummyAuthenticator, token refreshing is not applicable.
    This method is implemented as a no-op.

    Returns:
        None
    """
    pass

  def get_auth_headers(self) -> dict:
    """
    Retrieve authentication headers.

    Since no authentication is performed, this method returns an empty dictionary.

    Returns:
        dict: An empty dictionary.
    """
    return {}
