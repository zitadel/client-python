import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Set

import jwt

from zitadel_client.auth.oauth_authenticator import (
    OAuthAuthenticator,
    OAuthAuthenticatorBuilder,
)
from zitadel_client.auth.open_id import OpenId
from zitadel_client.transport_options import TransportOptions


class WebTokenAuthenticator(OAuthAuthenticator):
    """
    JWT-bearer authenticator using the JWT Bearer Grant (RFC 7523).

    Signs a short-lived JWT assertion with PyJWT and exchanges it at the
    provider's token endpoint for an access token. The exchange is sent through
    the SDK's shared transport; see :class:`OAuthAuthenticator` for the caching
    and HTTP-injection contract.
    """

    GRANT_TYPE = "urn:ietf:params:oauth:grant-type:jwt-bearer"

    def __init__(
        self,
        open_id: OpenId,
        client_id: str,
        auth_scopes: Set[str],
        jwt_issuer: str,
        jwt_subject: str,
        jwt_audience: str,
        private_key: str,
        jwt_lifetime: timedelta = timedelta(hours=1),
        jwt_algorithm: str = "RS256",
        key_id: Optional[str] = None,
    ):
        """
        Constructs a WebTokenAuthenticator.

        :param open_id: Resolved OpenID configuration for the provider.
        :param client_id: The OAuth2 client identifier.
        :param auth_scopes: The scope(s) for the token request.
        :param jwt_issuer: The JWT issuer (iss) claim.
        :param jwt_subject: The JWT subject (sub) claim.
        :param jwt_audience: The JWT audience (aud) claim.
        :param private_key: The PEM private key used to sign the JWT.
        :param jwt_lifetime: Lifetime of the JWT assertion.
        :param jwt_algorithm: The JWT signing algorithm (default "RS256").
        :param key_id: Optional key id (kid) header.
        """
        super().__init__(open_id, client_id, " ".join(auth_scopes))
        self.jwt_issuer = jwt_issuer
        self.jwt_subject = jwt_subject
        self.jwt_audience = jwt_audience
        self.private_key = private_key
        self.jwt_lifetime = jwt_lifetime
        self.jwt_algorithm = jwt_algorithm
        self.key_id = key_id

    def get_grant_type(self) -> str:
        return self.GRANT_TYPE

    def get_access_token_options(self) -> Dict[str, str]:
        """
        Builds the grant-specific parameters for the JWT-bearer flow.

        Dynamically generates a signed JWT assertion with time-sensitive claims.

        :raises Exception: If JWT generation fails.
        """
        now = datetime.now(timezone.utc)
        headers: Dict[str, str] = {}
        if self.key_id is not None:
            headers["kid"] = self.key_id
        try:
            assertion = jwt.encode(
                {
                    "iss": self.jwt_issuer,
                    "sub": self.jwt_subject,
                    "aud": self.jwt_audience,
                    "iat": int(now.timestamp()),
                    "exp": int((now + self.jwt_lifetime).timestamp()),
                },
                self.private_key,
                algorithm=self.jwt_algorithm,
                headers=headers,
            )
        except Exception as e:
            raise Exception("Failed to generate JWT assertion: " + str(e)) from e

        return {
            "scope": self.scope,
            "assertion": assertion,
        }

    @classmethod
    def from_json(
        cls,
        host: str,
        json_path: str,
        transport_options: Optional[TransportOptions] = None,
    ) -> "WebTokenAuthenticator":
        """
        Create a WebTokenAuthenticator from a service-account JSON file.

        Expected JSON format::

            {
                "type": "serviceaccount",
                "keyId": "<key-id>",
                "key": "<private-key>",
                "userId": "<user-id>"
            }

        :param host: Base URL for the API endpoints.
        :param json_path: File path to the JSON configuration file.
        :param transport_options: Optional transport options for TLS, proxy, and headers.
        :return: A new instance of WebTokenAuthenticator.
        :raises Exception: If the file cannot be read, the JSON is invalid,
                           or required keys are missing.
        """
        try:
            with open(json_path, "r") as file:
                config = json.load(file)
        except Exception as e:
            raise Exception(f"Unable to read JSON file: {json_path}") from e

        user_id = config.get("userId")
        private_key = config.get("key")
        key_id = config.get("keyId")
        if not user_id or not key_id or not private_key:
            raise Exception(
                "Missing required keys 'userId', 'keyId' or 'key' in JSON file."
            )

        return (
            WebTokenAuthenticator.builder(
                host, user_id, private_key, transport_options=transport_options
            )
            .key_identifier(key_id)
            .build()
        )

    @staticmethod
    def builder(
        host: str,
        user_id: str,
        private_key: str,
        transport_options: Optional[TransportOptions] = None,
    ) -> "WebTokenAuthenticatorBuilder":
        """
        Returns a builder for constructing a WebTokenAuthenticator.

        :param host: The base URL for the OAuth provider.
        :param user_id: The user identifier, used as both the issuer and subject.
        :param private_key: The private key used to sign the JWT.
        :param transport_options: Optional transport options for TLS, proxy, and headers.
        :return: A WebTokenAuthenticatorBuilder instance.
        """
        return WebTokenAuthenticatorBuilder(
            host,
            user_id,
            user_id,
            host,
            private_key,
            transport_options=transport_options,
        )


class WebTokenAuthenticatorBuilder(
    OAuthAuthenticatorBuilder["WebTokenAuthenticatorBuilder"]
):
    """
    Builder for WebTokenAuthenticator.

    Provides a fluent API for configuring and constructing a
    WebTokenAuthenticator instance.
    """

    def __init__(
        self,
        host: str,
        jwt_issuer: str,
        jwt_subject: str,
        jwt_audience: str,
        private_key: str,
        key_id: Optional[str] = None,
        transport_options: Optional[TransportOptions] = None,
    ):
        """
        Initializes the WebTokenAuthenticatorBuilder.

        :param host: The base URL for API endpoints.
        :param jwt_issuer: The issuer claim for the JWT.
        :param jwt_subject: The subject claim for the JWT.
        :param jwt_audience: The audience claim for the JWT.
        :param private_key: The PEM-formatted private key used for signing the JWT.
        :param key_id: Optional key id (kid) header.
        :param transport_options: Optional transport options for TLS, proxy, and headers.
        """
        super().__init__(host, transport_options=transport_options)
        self.jwt_issuer = jwt_issuer
        self.jwt_subject = jwt_subject
        self.jwt_audience = jwt_audience
        self.private_key = private_key
        self.jwt_lifetime = timedelta(hours=1)
        self.jwt_algorithm = "RS256"
        self.key_id = key_id

    def token_lifetime_seconds(self, seconds: int) -> "WebTokenAuthenticatorBuilder":
        """
        Sets the JWT token lifetime in seconds.

        :param seconds: Lifetime of the JWT in seconds.
        :return: The builder instance.
        """
        self.jwt_lifetime = timedelta(seconds=seconds)
        return self

    def jwt_algorithm_(self, jwt_algorithm: str) -> "WebTokenAuthenticatorBuilder":
        """
        Sets the JWT signing algorithm.

        :param jwt_algorithm: The signing algorithm (e.g. "RS256").
        :return: The builder instance.
        """
        self.jwt_algorithm = jwt_algorithm
        return self

    def key_identifier(self, key_id: Optional[str]) -> "WebTokenAuthenticatorBuilder":
        """
        Sets the optional key id (kid) header.

        :param key_id: The key identifier.
        :return: The builder instance.
        """
        self.key_id = key_id
        return self

    def build(self) -> WebTokenAuthenticator:
        """
        Builds and returns a new WebTokenAuthenticator instance.

        :return: A new WebTokenAuthenticator instance.
        """
        return WebTokenAuthenticator(
            open_id=self.open_id,
            client_id="zitadel",
            auth_scopes=self.auth_scopes,
            jwt_issuer=self.jwt_issuer,
            jwt_subject=self.jwt_subject,
            jwt_audience=self.jwt_audience,
            private_key=self.private_key,
            jwt_lifetime=self.jwt_lifetime,
            jwt_algorithm=self.jwt_algorithm,
            key_id=self.key_id,
        )
