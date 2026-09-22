import json
import time
from abc import ABC, abstractmethod
from threading import RLock
from typing import Any, Dict, Generic, Optional, TypeVar
from urllib.parse import urlencode

from zitadel_client.api_client import ApiClient
from zitadel_client.auth.base_authenticator import BaseAuthenticator
from zitadel_client.auth.http_aware_authenticator import HttpAwareAuthenticator
from zitadel_client.auth.open_id import OpenId
from zitadel_client.errors.oauth2_server_exception import OAuth2ServerException
from zitadel_client.errors.oauth2_token_exception import OAuth2TokenException

DEFAULT_SCOPE = "openid urn:zitadel:iam:org:project:id:zitadel:aud"


def require_text(value: Optional[str], label: str) -> str:
    """Raise :class:`ValueError` when the value is ``None`` or blank."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} cannot be empty.")
    return value


def _parse_object(body: str) -> Optional[Dict[str, Any]]:
    try:
        payload = json.loads(body)
    except ValueError:
        return None
    return payload if isinstance(payload, dict) else None


class OAuthAuthenticator(BaseAuthenticator, HttpAwareAuthenticator, ABC):
    """
    Abstract base class for OAuth-based, token-minting authenticators.

    Mints a bearer token by POSTing an OAuth2 grant (client-credentials or a
    signed JWT-bearer assertion) to the provider's token endpoint, then
    attaches the resulting access token on every API request. The minted token
    is cached together with its expiry and only re-minted once it is within the
    refresh skew of expiring.

    Token-minting requires an outbound HTTP call, so this class implements
    :class:`HttpAwareAuthenticator`: the shared :class:`ApiClient` is injected
    by the :class:`zitadel_client.zitadel.Zitadel` constructor and both OpenID
    discovery and the token POST are sent through it. A token request fails
    with:

    - :class:`RuntimeError` when no :class:`ApiClient` has been injected;
    - :class:`NetworkException` or :class:`NetworkTimeoutException` when no
      HTTP response arrived;
    - :class:`OAuth2ServerException` when the token endpoint answered with a
      non-2xx status;
    - :class:`OAuth2TokenException` when it answered 2xx without a usable
      access token.
    """

    # Seconds before expiry at which a cached token is treated as stale.
    REFRESH_SKEW_SECONDS = 300

    def __init__(self, open_id: OpenId, scope: str):
        """
        Constructs an OAuthAuthenticator.

        :param open_id: The OpenID discovery helper for the target host.
        :param scope: Space-delimited scope string for the token request.
        """
        self.open_id = open_id
        self.scope = scope
        self._api_client: Optional[ApiClient] = None
        self._access_token: Optional[str] = None
        self._expires_at: Optional[float] = None
        self._lock = RLock()

    def set_api_client(self, api_client: ApiClient) -> None:
        self._api_client = api_client

    def get_host(self) -> str:
        return self.open_id.get_host_endpoint()

    def get_auth_headers(self) -> Dict[str, str]:
        return {"Authorization": "Bearer " + self.get_auth_token()}

    def get_auth_token(self) -> str:
        """
        Return a valid access token, minting (or re-minting) one if the cache
        is empty or within the refresh skew of expiring.
        """
        with self._lock:
            token = self._access_token
            if token is None or self._is_stale():
                token = self.refresh_token()
            return token

    def _is_stale(self) -> bool:
        return (
            self._expires_at is not None
            and time.time() >= self._expires_at - self.REFRESH_SKEW_SECONDS
        )

    def refresh_token(self) -> str:
        """
        Exchange the configured grant for a fresh access token and cache it.

        :return: The freshly minted access token.
        """
        with self._lock:
            api_client = self._api_client
            if api_client is None:
                raise RuntimeError(
                    "OAuthAuthenticator has no ApiClient; use it through the Zitadel client, which injects one before the first token request."
                )

            params: Dict[str, str] = {
                "grant_type": self.get_grant_type(),
                "scope": self.scope,
            }
            params.update(self.get_token_request_params())

            response = api_client.send_request(
                "POST",
                self.open_id.get_token_endpoint(api_client),
                {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
                urlencode(params),
                # never replay a token POST across a redirect: a malicious
                # 307/308 could otherwise leak the assertion or secret.
                True,
            )

            status = response.status_code
            if status < 200 or status >= 300:
                raise self._server_error(status, response.body)

            payload = _parse_object(response.body)
            if payload is None:
                raise OAuth2TokenException("Token response is not a JSON object")
            access_token = payload.get("access_token")
            if not isinstance(access_token, str) or not access_token:
                raise OAuth2TokenException(
                    "Token response missing or empty access_token field"
                )
            expires_in = payload.get("expires_in")
            if (
                isinstance(expires_in, (int, float))
                and not isinstance(expires_in, bool)
                and expires_in > 0
            ):
                self._expires_at = time.time() + float(expires_in)
            else:
                self._expires_at = None
            self._access_token = access_token
            return access_token

    @staticmethod
    def _server_error(status: int, body: str) -> OAuth2ServerException:
        payload = _parse_object(body)
        code = payload.get("error") if payload is not None else None
        if payload is None or not isinstance(code, str) or not code:
            return OAuth2ServerException(status, None, None, None, body)
        description = payload.get("error_description")
        uri = payload.get("error_uri")
        return OAuth2ServerException(
            status,
            code,
            description if isinstance(description, str) else None,
            uri if isinstance(uri, str) else None,
            body,
        )

    def _masked_token(self) -> Optional[str]:
        return "***" if self._access_token is not None else None

    def __repr__(self) -> str:
        # Mask the cached token so it never leaks through repr() / logging.
        return f"{type(self).__name__}(host={self.get_host()!r}, scope={self.scope!r}, access_token={self._masked_token()!r})"

    @abstractmethod
    def get_grant_type(self) -> str:
        """The OAuth2 grant_type value sent in the token request."""
        ...  # pragma: no cover

    @abstractmethod
    def get_token_request_params(self) -> Dict[str, str]:
        """Grant-specific token-request parameters (e.g. assertion)."""
        ...  # pragma: no cover


T = TypeVar("T", bound="OAuthAuthenticatorBuilder[Any]")


class OAuthAuthenticatorBuilder(ABC, Generic[T]):
    """
    Abstract builder class for constructing OAuth authenticator instances.

    Holds the OpenID discovery helper for the host and the requested scopes.
    """

    def __init__(self, host: str):
        """
        Initializes the OAuthAuthenticatorBuilder with a given host.

        :param host: The base URL for the OAuth provider.
        :raises ValueError: If the host is not a valid http or https URL.
        """
        super().__init__()
        self.open_id = OpenId(host)
        self.scope = DEFAULT_SCOPE

    def scopes(self: T, *auth_scopes: str) -> T:
        """
        Overrides the default scopes. Duplicates are dropped; order is kept.

        :param auth_scopes: The scopes for the token request.
        :return: The builder instance to allow for method chaining.
        :raises ValueError: If no scope is given, or a scope is empty or
            contains whitespace.
        """
        if not auth_scopes:
            raise ValueError("At least one scope is required.")
        unique: Dict[str, None] = {}
        for auth_scope in auth_scopes:
            if (
                not isinstance(auth_scope, str)
                or not auth_scope
                or any(c.isspace() for c in auth_scope)
            ):
                raise ValueError(
                    f"Scope must be a non-empty string without whitespace: '{auth_scope}'"
                )
            unique[auth_scope] = None
        self.scope = " ".join(unique)
        return self
