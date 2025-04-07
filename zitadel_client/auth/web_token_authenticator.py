from datetime import datetime, timedelta, timezone

from authlib.integrations.requests_client import OAuth2Session
from authlib.jose import jwt, JoseError

from zitadel_client.auth.authenticator import OAuthAuthenticatorBuilder
from zitadel_client.auth.oauth_authenticator import OAuthAuthenticator
from zitadel_client.auth.open_id import OpenId


class JWTAuthenticator(OAuthAuthenticator):
  """
  OAuth authenticator implementing the JWT bearer flow.

  This implementation builds a JWT assertion dynamically in get_grant().
  """

  def __init__(self, open_id: OpenId, auth_scopes: str,
               jwt_issuer: str, jwt_subject: str, jwt_audience: str,
               private_key: str, jwt_lifetime: timedelta = timedelta(hours=1), jwt_algorithm: str = "RS256"):
    """
    Constructs a JWTAuthenticator.

    :param open_id: The base URL for the OAuth provider.
    :param auth_scopes: The scope(s) for the token request.
    :param jwt_issuer: The JWT issuer.
    :param jwt_subject: The JWT subject.
    :param jwt_audience: The JWT audience.
    :param private_key: The private key used to sign the JWT.
    :param jwt_lifetime: Lifetime of the JWT in seconds.
    :param jwt_algorithm: The JWT signing algorithm (default "RS256").
    """
    super().__init__(open_id, OAuth2Session(scope=auth_scopes))
    self.jwt_issuer = jwt_issuer
    self.jwt_subject = jwt_subject
    self.jwt_audience = jwt_audience
    self.private_key = private_key
    self.jwt_lifetime = jwt_lifetime
    self.jwt_algorithm = jwt_algorithm

  def get_grant(self) -> dict:
    """
    Builds and returns the grant parameters for the JWT bearer flow.

    Dynamically generates a JWT assertion that includes time-sensitive claims.

    :return: A dictionary with the JWT bearer grant parameters.
    :raises Exception: If JWT generation fails.
    """
    now = datetime.now(timezone.utc)
    try:
      return {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": (jwt.encode({"alg": self.jwt_algorithm, "typ": "JWT"}, {
          "iss": self.jwt_issuer,
          "sub": self.jwt_subject,
          "aud": self.jwt_audience,
          "iat": int(now.timestamp()),
          "exp": int((now + self.jwt_lifetime).timestamp())
        }, self.private_key, algorithm=self.jwt_algorithm))
      }
    except JoseError as e:
      raise Exception("Failed to generate JWT assertion: " + str(e)) from e

  @staticmethod
  def builder(host: str, user_id: str, private_key: str) -> "JWTAuthenticatorBuilder":
    """
    Returns a builder for constructing a JWTAuthenticator.

    :param host: The base URL for the OAuth provider.
    :param user_id: The user identifier, used as both the issuer and subject.
    :param private_key: The private key used to sign the JWT.
    :return: A JWTAuthenticatorBuilder instance.
    """
    return JWTAuthenticatorBuilder(host, user_id, user_id, host, private_key)


class JWTAuthenticatorBuilder(OAuthAuthenticatorBuilder):
  """
  Builder for JWTAuthenticator.

  Provides a fluent API for configuring and constructing a JWTAuthenticator instance.
  """

  def __init__(self, host: str, jwt_issuer: str, jwt_subject: str, jwt_audience: str, private_key: str):
    """
    Initializes the JWTAuthenticatorBuilder with required parameters.

    :param host: The base URL for API endpoints.
    :param jwt_issuer: The issuer claim for the JWT.
    :param jwt_subject: The subject claim for the JWT.
    :param jwt_audience: The audience claim for the JWT.
    :param private_key: The PEM-formatted private key used for signing the JWT.
    """
    super().__init__(host)
    self.jwt_issuer = jwt_issuer
    self.jwt_subject = jwt_subject
    self.jwt_audience = jwt_audience
    self.private_key = private_key
    self.jwt_lifetime = timedelta(hours=1)

  def token_lifetime_seconds(self, seconds: int) -> "JWTAuthenticatorBuilder":
    """
    Sets the JWT token lifetime in seconds.

    :param seconds: Lifetime of the JWT in seconds.
    :return: The builder instance.
    """
    self.jwt_lifetime = timedelta(seconds=seconds)
    return self

  def scopes(self, scopes: set) -> "JWTAuthenticatorBuilder":
    """
    Overrides the default scopes for the JWTAuthenticator.

    :param scopes: A set of scope strings.
    :return: The builder instance.
    """
    self.auth_scopes = " ".join(scopes)
    return self

  def build(self) -> JWTAuthenticator:
    """
    Builds and returns a new JWTAuthenticator instance using the configured parameters.

    This method inlines the JWT assertion generation logic and passes all required
    configuration to the JWTAuthenticator constructor.

    :return: A new JWTAuthenticator instance.
    """
    return JWTAuthenticator(
      open_id=self.open_id,
      auth_scopes=self.auth_scopes,
      jwt_issuer=self.jwt_issuer,
      jwt_subject=self.jwt_subject,
      jwt_audience=self.jwt_audience,
      private_key=self.private_key,
      jwt_lifetime=self.jwt_lifetime
    )
