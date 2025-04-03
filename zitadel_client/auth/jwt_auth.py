import json
import time

from authlib.integrations.requests_client import OAuth2Session
from authlib.jose import jwt

from zitadel_client.auth.oauth_base import OAuthAuthenticator


class JWTAuthenticator(OAuthAuthenticator):
  """
  An Authenticator implementation using JWT-based authentication (RFC7523).

  This strategy leverages Authlib's JOSE support to create a JWT assertion,
  which is then exchanged for an access token via the token endpoint using
  the JWT bearer grant.
  """

  def __init__(self, host: str, client_id: str, issuer: str, subject: str,
               audience: str, private_key: str, token_url: str = "/oauth/v2/token", algorithm: str = "RS256",
               token_lifetime: int = 300):
    """
    Initialize the JWTAuthenticator with the required credentials and claims.

    Args:
        host (str): The base URL for the API endpoints.
        client_id (str): The OAuth2 client identifier.
        token_url (str): The URL of the OAuth2 token endpoint.
        issuer (str): The issuer claim for the JWT.
        subject (str): The subject claim for the JWT.
        audience (str): The audience claim, typically the token endpoint URL.
        private_key (str): The private key used to sign the JWT.
        algorithm (str, optional): The signing algorithm. Defaults to "RS256".
        token_lifetime (int, optional): Lifetime of the JWT in seconds. Defaults to 300.
    """
    # token_url might be relative
    super().__init__(host, client_id, token_url)
    self.issuer = issuer
    self.subject = subject
    self.audience = audience
    self.private_key = private_key
    self.algorithm = algorithm
    self.token_lifetime = token_lifetime
    self.session = OAuth2Session(client_id)

  def _generate_jwt_assertion(self) -> str:
    """
    Generate a JWT assertion based on the provided credentials and claims.

    Returns:
        str: A signed JWT assertion.
    """
    current_time = int(time.time())
    payload = {
      "iss": self.issuer,
      "sub": self.subject,
      "aud": self.audience,
      "iat": current_time,
      "exp": current_time + self.token_lifetime,
      "jti": str(current_time)
    }
    header = {"alg": self.algorithm, "typ": "JWT"}
    assertion = jwt.encode(header, payload, self.private_key)
    return assertion.decode("utf-8") if isinstance(assertion, bytes) else assertion

  def refresh_token(self) -> None:
    """
    Refresh the access token using a JWT assertion.

    This method generates a new JWT assertion and exchanges it for an access token
    via the token endpoint using the JWT bearer grant.
    """
    jwt_assertion = self._generate_jwt_assertion()
    self.token = self.session.fetch_token(
      grant_type="urn:ietf:params:oauth:grant-type:jwt-bearer",
      assertion=jwt_assertion,
      client_id=self.client_id
    )

  @classmethod
  def from_json(cls, json_path: str, host: str, token_url: str, audience: str,
                algorithm: str = "RS256", token_lifetime: int = 300):
    """
    Initialize a JWTAuthenticator instance from a JSON configuration file.

    The JSON file should have the following structure:

    {
        "type": "serviceaccount",
        "keyId": "100509901696068329",
        "key": "-----BEGIN RSA PRIVATE KEY----- [...] -----END RSA PRIVATE KEY-----\n",
        "userId": "100507859606888466"
    }

    Args:
        json_path (str): The file path to the JSON configuration file.
        host (str): The base URL for the API endpoints.
        token_url (str): The URL of the OAuth2 token endpoint.
        audience (str): The custom domain to be used as the 'aud' claim.
        algorithm (str, optional): The signing algorithm. Defaults to "RS256".
        token_lifetime (int, optional): Lifetime of the JWT in seconds. Defaults to 300.

    Returns:
        JWTAuthenticator: An initialized instance of JWTAuthenticator.
    """
    with open(json_path, 'r') as f:
      config = json.load(f)

    user_id = config.get("userId")
    private_key = config.get("key")
    return cls(
      host=host,
      client_id=user_id,
      token_url=token_url,
      issuer=user_id,
      subject=user_id,
      audience=audience,
      private_key=private_key,
      algorithm=algorithm,
      token_lifetime=token_lifetime
    )
