from authlib.integrations.requests_client import OAuth2Session

from .oauth_base import OAuthAuthenticator


class ClientCredentialsAuthenticator(OAuthAuthenticator):
  """
  An Authenticator implementation using the OAuth2 client credentials grant.

  This class leverages the Authlib library to perform the client credentials flow.
  It retrieves an access token from the token endpoint and provides it as part of the
  authentication header for subsequent API requests.
  """

  def __init__(
    self,
    host: str,
    client_id: str,
    client_secret: str,
    token_url: str = "/oauth/v2/token",
    scope: str = "openid urn:zitadel:iam:org:project:id:myprojectid:aud additional_scope"  # FIXME
  ):
    """
    Initialize the ClientCredentialsAuthenticator with client credentials.

    Args:
        host (str): The base URL for the API endpoints.
        client_id (str): The OAuth2 client identifier.
        client_secret (str): The OAuth2 client secret.
        token_url (str, optional): The URL of the OAuth2 token endpoint.
            Defaults to "/oauth/v2/token".
        scope (str, optional): The scope for the token request.
            Defaults to a string containing "openid" and additional required scopes.
    """
    # If token_url is relative, prepend the host.
    super().__init__(host, client_id, token_url, scope)
    self.client_secret = client_secret
    self.session = OAuth2Session(client_id, client_secret=client_secret, scope=scope)

  def refresh_token(self) -> None:
    """
    Refresh the access token using the OAuth2 client credentials grant.

    This method fetches a new access token from the token endpoint using the
    client credentials and updates the stored token.
    """
    self.token = self.session.fetch_token(
      grant_type="client_credentials"
    )
