from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from authlib.integrations.requests_client import OAuth2Session

from zitadel_client.auth.authenticator import Token, Authenticator
from zitadel_client.auth.open_id import OpenId


class OAuthAuthenticator(Authenticator, ABC):
  """
  Base class for OAuth-based authentication using Authlib.

  Attributes:
      open_id: An object providing OAuth endpoint information.
      oauth_session: An OAuth2Session instance used for fetching tokens.
  """

  def __init__(self, open_id: OpenId, oauth_session: OAuth2Session):
    """
    Constructs an OAuthAuthenticator.

    :param open_id: An object that must implement get_host_endpoint() and get_token_endpoint().
    :param oauth_session: The scope for the token request.
    """
    super().__init__(open_id.get_host_endpoint())
    self.open_id = open_id
    self.token: Optional[Token] = None
    self.oauth_session = oauth_session

  def get_auth_token(self) -> str:
    """
    Returns the current access token, refreshing it if necessary.
    """
    if self.token is None or self.token.is_expired():
      self.refresh_token()
    return self.token.access_token

  def get_auth_headers(self) -> Dict[str, str]:
    """
    Retrieves authentication headers.

    :return: A dictionary containing the 'Authorization' header.
    """
    return {"Authorization": "Bearer " + self.get_auth_token()}

  @abstractmethod
  def get_grant(self) -> dict:
    """
    Builds and returns a dictionary of grant parameters required for the token request.

    For example, this might include parameters like grant_type, client_assertion, etc.
    """
    pass

  def refresh_token(self) -> Token:
    """
    Refreshes the access token using the OAuth flow.
    It uses get_grant() to obtain all necessary parameters, such as the grant type and any assertions.

    :return: A new Token.
    """
    try:
      token_response = self.oauth_session.fetch_token(url=(self.open_id.get_token_endpoint()), **(self.get_grant()))
      access_token = token_response["access_token"]
      expires_in = token_response.get("expires_in", 3600)
      expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
      self.token = Token(access_token, expires_at)
      return self.token
    except Exception as e:
      raise Exception("Failed to refresh token: " + str(e)) from e
