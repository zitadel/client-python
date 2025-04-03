from authlib.integrations.requests_client import OAuth2Session

from .authenticator import Authenticator


class OAuthAuthenticator(Authenticator):
  """
  Abstract base class for OAuth-based authenticators.

  Attributes:
      client_id (str): The OAuth2 client identifier.
      token_url (str): The URL of the OAuth2 token endpoint.
      scope (str): The scope for the token request.
      session (OAuth2Session): The OAuth2 session instance used for token management.
      token (dict): The most recently retrieved access token.
  """

  def __init__(self, host: str, client_id: str, token_url: str, scope: str = None):
    """
    Initialize the OAuthAuthenticator with the basic OAuth2 parameters.

    Args:
        host (str): The base URL for the API endpoints.
        client_id (str): The OAuth2 client identifier.
        token_url (str): The URL of the OAuth2 token endpoint.
        scope (str, optional): The scope for the token request.
    """
    super().__init__(host)
    self.client_id = client_id
    self.token_url = f"{host}{token_url}" if token_url.startswith("/") else token_url
    self.scope = scope
    self.session = OAuth2Session(client_id, scope=scope, token_endpoint=token_url)
    self.token = None

  def get_auth_headers(self) -> dict:
    """
    Retrieve the authentication headers using the OAuth2 flow.

    This method checks whether a valid access token is available. If no token exists
    or if the current token is expired, it refreshes the token by calling `refresh_token()`.
    It then returns an HTTP header with the Bearer token.

    Returns:
        dict: A dictionary containing the 'Authorization' header.
    """
    if not self.token or self.session.token.is_expired():
      self.refresh_token()
    return {"Authorization": f"Bearer {self.token['access_token']}"}

  def refresh_token(self) -> None:
    """
    Abstract method to refresh the access token.

    Subclasses must implement this method to perform the token refresh using their
    specific grant flow.
    """
    raise NotImplementedError("Subclasses must implement refresh_token()")
