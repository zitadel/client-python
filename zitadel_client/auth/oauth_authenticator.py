import json
import time
from abc import ABC, abstractmethod
from threading import Lock
from typing import Any, Dict, Generic, Optional, TypeVar
from urllib.parse import urlencode

from zitadel_client.api_client import ApiClient
from zitadel_client.auth.base_authenticator import BaseAuthenticator
from zitadel_client.auth.http_aware_authenticator import HttpAwareAuthenticator
from zitadel_client.auth.open_id import OpenId
from zitadel_client.errors import ApiException
from zitadel_client.transport_options import TransportOptions


class OAuthAuthenticator(BaseAuthenticator, HttpAwareAuthenticator, ABC):
    """
    Abstract base class for OAuth-based, token-minting authenticators.

    Mints a bearer token by POSTing an OAuth2 grant (client-credentials or a
    signed JWT-bearer assertion) to the provider's token endpoint, then
    attaches the resulting access token on every API request. The minted token
    is cached together with its expiry and only re-minted once it is within the
    refresh skew of expiring.

    Token-minting requires an outbound HTTP call, so this class implements
    :class:`HttpAwareAuthenticator`: the :class:`ApiClient` is injected by the
    :class:`zitadel_client.client.Client` constructor and the token POST is
    sent through it. Sharing the SDK transport means token exchange honours the
    same proxy, TLS, timeout and redirect configuration as regular API calls.

    (Previously this exchange went through authlib's ``OAuth2Session``; that
    dependency has been dropped in favour of the injected SDK transport. A JWT
    library is retained only for signing the JWT-bearer assertion.)
    """

    # Seconds before expiry at which a cached token is treated as stale and
    # re-minted. Mirrors the previous 5-minute skew.
    REFRESH_SKEW_SECONDS = 300

    def __init__(
        self,
        open_id: OpenId,
        client_id: str,
        scope: str,
    ):
        """
        Constructs an OAuthAuthenticator.

        :param open_id: Resolved OpenID configuration (host + token endpoint).
        :param client_id: The OAuth2 client identifier.
        :param scope: Space-delimited scope string for the token request.
        """
        self.open_id = open_id
        self.client_id = client_id
        self.scope = scope
        self._api_client: Optional[ApiClient] = None
        self._access_token: Optional[str] = None
        self._expires_at: float = 0.0
        self._lock = Lock()

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

        :raises ApiException: If the token cannot be obtained.
        """
        with self._lock:
            if self._access_token is None or (
                self._expires_at != 0
                and time.time() >= (self._expires_at - self.REFRESH_SKEW_SECONDS)
            ):
                self.refresh_token()

            if self._access_token is None:
                raise ApiException(
                    message="Token is null even after attempting to refresh."
                )
            token = self._access_token
        return token

    def refresh_token(self) -> str:
        """
        Exchange the configured grant for a fresh access token and cache it.

        POSTs an ``application/x-www-form-urlencoded`` body to the token
        endpoint through the injected :class:`ApiClient`. Subclasses contribute
        the grant_type and the grant-specific parameters (scope, assertion, ...).

        :return: The freshly minted access token.
        :raises ApiException: If the client is not yet injected or the
                              exchange fails.
        """
        if self._api_client is None:
            raise ApiException(
                message=(
                    "OAuthAuthenticator has no ApiClient; it must be used via zitadel_client.client.Client, which injects the shared transport before any token exchange."
                )
            )

        params: Dict[str, str] = {"grant_type": self.get_grant_type()}
        params.update(self.get_access_token_options())

        response = self._api_client.send_request(
            "POST",
            self.open_id.get_token_endpoint(),
            {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            urlencode(params),
            # no_redirect: never replay a token POST across a redirect — a
            # malicious 307/308 could otherwise leak the assertion/secret.
            True,
        )

        if response.status_code < 200 or response.status_code >= 300:
            raise ApiException(
                status_code=response.status_code,
                message=f"Token refresh failed: token endpoint returned HTTP {response.status_code}",
                response_headers=response.headers,
                response_body=response.body,
            )

        try:
            payload = json.loads(response.body)
        except json.JSONDecodeError as e:
            raise ApiException(
                status_code=response.status_code,
                message="Token refresh failed: token endpoint response was not valid JSON.",
                response_headers=response.headers,
                response_body=response.body,
            ) from e

        if not isinstance(payload, dict) or not isinstance(
            payload.get("access_token"), str
        ):
            raise ApiException(
                status_code=response.status_code,
                message="Token refresh failed: token endpoint response did not contain an access_token.",
                response_headers=response.headers,
                response_body=response.body,
            )

        access_token: str = payload["access_token"]
        self._access_token = access_token
        expires_in = payload.get("expires_in")
        if isinstance(expires_in, (int, float)) and expires_in > 0:
            self._expires_at = time.time() + float(expires_in)
        else:
            self._expires_at = 0.0

        return access_token

    def __repr__(self) -> str:
        # Mask the cached token so it never leaks through repr() / logging.
        masked = "***" if self._access_token is not None else None
        return f"{type(self).__name__}(host={self.get_host()!r}, client_id={self.client_id!r}, scope={self.scope!r}, access_token={masked!r}, expires_at={self._expires_at!r})"

    @abstractmethod
    def get_grant_type(self) -> str:
        """The OAuth2 grant_type value sent in the token request."""
        ...  # pragma: no cover

    @abstractmethod
    def get_access_token_options(self) -> Dict[str, str]:
        """Grant-specific token-request parameters (e.g. scope, assertion)."""
        ...  # pragma: no cover


T = TypeVar("T", bound="OAuthAuthenticatorBuilder[Any]")


class OAuthAuthenticatorBuilder(ABC, Generic[T]):
    """
    Abstract builder class for constructing OAuth authenticator instances.

    Provides common configuration options such as the resolved OpenId instance
    and authentication scopes.
    """

    def __init__(
        self,
        host: str,
        transport_options: Optional[TransportOptions] = None,
    ):
        """
        Initializes the OAuthAuthenticatorBuilder with a given host.

        :param host: The base URL for the OAuth provider.
        :param transport_options: Optional transport options for TLS, proxy, and headers.
        """
        super().__init__()
        self.transport_options = transport_options or TransportOptions.builder().build()
        self.open_id = OpenId(host, transport_options=self.transport_options)
        self.auth_scopes = {"openid", "urn:zitadel:iam:org:project:id:zitadel:aud"}

    def scopes(self: T, *auth_scopes: str) -> T:
        """
        Sets the authentication scopes for the OAuth authenticator.

        :param auth_scopes: A variable number of scope strings.
        :return: The builder instance to allow for method chaining.
        """
        self.auth_scopes = set(auth_scopes)
        return self
