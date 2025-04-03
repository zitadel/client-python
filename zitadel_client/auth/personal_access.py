from .authenticator import Authenticator


class PersonalAccessAuthenticator(Authenticator):
  """
  Authenticator implementation using a personal access token.

  This strategy simply injects the personal access token into the HTTP
  Authorization header for API requests.
  """

  def __init__(self, host: str, token: str):
    """
    Initialize the authenticator with a personal access token.

    Args:
        host (str): The base URL for the API endpoints.
        token (str): The personal access token to be used for authentication.
    """
    super().__init__(host)
    self.token = token

  def refresh_token(self) -> None:
    """
    Refresh the authentication token.

    For PersonalAccessAuthenticator, token refresh is not applicable as the token
    is static. This method is implemented as a no-op.

    Returns:
        None
    """
    pass

  def get_auth_headers(self) -> dict:
    """
    Retrieve authentication headers using the personal access token.

    Returns:
        dict: A dictionary with the 'Authorization' header.
              Example: {'Authorization': 'Bearer <token>'}
    """
    return {"Authorization": f"Bearer {self.token}"}
