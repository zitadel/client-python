import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Set

from authlib.integrations.requests_client import OAuth2Session
from authlib.jose import JoseError, jwt

from zitadel_client.auth.oauth_authenticator import (
    OAuthAuthenticator,
    OAuthAuthenticatorBuilder,
)
from zitadel_client.auth.open_id import OpenId


class WebTokenAuthenticator(OAuthAuthenticator):
    """
    OAuth authenticator implementing the JWT bearer flow.

    This implementation builds a JWT assertion dynamically in get_grant().
    """

    def __init__(
        self,
        open_id: OpenId,
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
        super().__init__(open_id, OAuth2Session(scope=" ".join(auth_scopes)))
        self.jwt_issuer = jwt_issuer
        self.jwt_subject = jwt_subject
        self.jwt_audience = jwt_audience
        self.private_key = private_key
        self.jwt_lifetime = jwt_lifetime
        self.jwt_algorithm = jwt_algorithm
        self.key_id = key_id

    def get_grant(self) -> Dict[str, str]:
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
                "assertion": (
                    jwt.encode(
                        {
                            "alg": self.jwt_algorithm,
                            "typ": "JWT",
                            "kid": self.key_id,
                        },
                        {
                            "iss": self.jwt_issuer,
                            "sub": self.jwt_subject,
                            "aud": self.jwt_audience,
                            "iat": int(now.timestamp()),
                            "exp": int((now + self.jwt_lifetime).timestamp()),
                        },
                        self.private_key,
                    )
                ),
            }
        except JoseError as e:
            raise Exception("Failed to generate JWT assertion: " + str(e)) from e

    @classmethod
    def from_json(cls, host: str, json_path: str) -> "WebTokenAuthenticator":
        """
        Create a WebTokenAuthenticatorBuilder instance from a JSON configuration file.

        Expected JSON format:
        {
            "type": "serviceaccount",
            "keyId": "<key-id>",
            "key": "<private-key>",
            "userId": "<user-id>"
        }

        :param host: Base URL for the API endpoints.
        :param json_path: File path to the JSON configuration file.
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
            raise Exception("Missing required keys 'userId', 'key_id' or 'key' in JSON file.")

        return (WebTokenAuthenticator.builder(host, user_id, private_key)).key_identifier(key_id).build()

    @staticmethod
    def builder(host: str, user_id: str, private_key: str) -> "WebTokenAuthenticatorBuilder":
        """
        Returns a builder for constructing a JWTAuthenticator.

        :param host: The base URL for the OAuth provider.
        :param user_id: The user identifier, used as both the issuer and subject.
        :param private_key: The private key used to sign the JWT.
        :return: A JWTAuthenticatorBuilder instance.
        """
        return WebTokenAuthenticatorBuilder(host, user_id, user_id, host, private_key)


class WebTokenAuthenticatorBuilder(OAuthAuthenticatorBuilder["WebTokenAuthenticatorBuilder"]):
    """
    Builder for JWTAuthenticator.

    Provides a fluent API for configuring and constructing a JWTAuthenticator instance.
    """

    def __init__(
        self,
        host: str,
        jwt_issuer: str,
        jwt_subject: str,
        jwt_audience: str,
        private_key: str,
        key_id: Optional[str] = None,
    ):
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
        self.key_id = key_id

    def token_lifetime_seconds(self, seconds: int) -> "WebTokenAuthenticatorBuilder":
        """
        Sets the JWT token lifetime in seconds.

        :param seconds: Lifetime of the JWT in seconds.
        :return: The builder instance.
        """
        self.jwt_lifetime = timedelta(seconds=seconds)
        return self

    def build(self) -> WebTokenAuthenticator:
        """
        Builds and returns a new JWTAuthenticator instance using the configured parameters.

        This method inlines the JWT assertion generation logic and passes all required
        configuration to the JWTAuthenticator constructor.

        :return: A new JWTAuthenticator instance.
        """
        return WebTokenAuthenticator(
            open_id=self.open_id,
            auth_scopes=self.auth_scopes,
            jwt_issuer=self.jwt_issuer,
            jwt_subject=self.jwt_subject,
            jwt_audience=self.jwt_audience,
            private_key=self.private_key,
            jwt_lifetime=self.jwt_lifetime,
            key_id=self.key_id,
        )

    def key_identifier(self, key_id: Optional[str]) -> "WebTokenAuthenticatorBuilder":
        self.key_id = key_id
        return self
