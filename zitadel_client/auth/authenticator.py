from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict

from zitadel_client.auth.open_id import OpenId


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
    pass

  def get_host(self) -> str:
    """
    Returns the stored host.

    :return: The host as a string.
    """
    return self.host


class Token:
  def __init__(self, access_token: str, expires_at: datetime):
    self.access_token = access_token
    self.expires_at = expires_at

  def is_expired(self) -> bool:
    return datetime.now(timezone.utc) >= self.expires_at


class OAuthAuthenticatorBuilder(ABC):
  """
  Abstract builder class for constructing OAuth authenticator instances.

  This builder provides common configuration options such as the OpenId instance and authentication scopes.
  """

  def __init__(self, host: str):
    """
    Initializes the OAuthAuthenticatorBuilder with a given host.

    :param host: The base URL for the OAuth provider.
    """
    self.open_id = OpenId(host)
    self.auth_scopes = "openid urn:zitadel:iam:org:project:id:zitadel:aud"

  def scopes(self, auth_scopes: set) -> "OAuthAuthenticatorBuilder":
    """
    Sets the authentication scopes for the OAuth authenticator.

    :param auth_scopes: A set of scope strings.
    :return: The builder instance to allow for method chaining.
    """
    self.auth_scopes = " ".join(auth_scopes)
    return self
