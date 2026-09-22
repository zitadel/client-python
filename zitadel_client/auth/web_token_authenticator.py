import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from jwt.algorithms import RSAAlgorithm

from zitadel_client.auth.oauth_authenticator import (
    OAuthAuthenticator,
    OAuthAuthenticatorBuilder,
    require_text,
)
from zitadel_client.auth.open_id import OpenId

_ALGORITHMS = ("RS256", "RS384", "RS512")


def _load_private_key(private_key: str) -> Any:
    """Parse a PEM-encoded RSA private key, raising :class:`ValueError` otherwise."""
    try:
        key = RSAAlgorithm(RSAAlgorithm.SHA256).prepare_key(private_key)
    except Exception as e:
        raise ValueError("Private key is not a valid RSA private key.") from e
    if not hasattr(key, "private_numbers"):
        raise ValueError("Private key is not a valid RSA private key.")
    return key


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
        scope: str,
        jwt_issuer: str,
        jwt_subject: str,
        jwt_audience: str,
        private_key: Any,
        jwt_lifetime: timedelta = timedelta(hours=1),
        jwt_algorithm: str = "RS256",
        key_id: Optional[str] = None,
    ):
        """
        Constructs a WebTokenAuthenticator.

        :param open_id: The OpenID discovery helper for the target host.
        :param scope: Space-delimited scope string for the token request.
        :param jwt_issuer: The JWT issuer (iss) claim.
        :param jwt_subject: The JWT subject (sub) claim.
        :param jwt_audience: The JWT audience (aud) claim.
        :param private_key: The RSA private key used to sign the JWT.
        :param jwt_lifetime: Lifetime of the JWT assertion.
        :param jwt_algorithm: The JWT signing algorithm (default "RS256").
        :param key_id: Optional key id (kid) header.
        """
        super().__init__(open_id, scope)
        self.jwt_issuer = jwt_issuer
        self.jwt_subject = jwt_subject
        self.jwt_audience = jwt_audience
        self.private_key = private_key
        self.jwt_lifetime = jwt_lifetime
        self.jwt_algorithm = jwt_algorithm
        self.key_id = key_id

    def get_grant_type(self) -> str:
        return self.GRANT_TYPE

    def get_token_request_params(self) -> Dict[str, str]:
        """
        Builds the grant-specific parameters for the JWT-bearer flow: a freshly
        signed JWT assertion with time-sensitive claims.
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
            raise RuntimeError("Unable to sign the JWT assertion") from e
        return {"assertion": assertion}

    @classmethod
    def from_json(cls, host: str, json_path: str) -> "WebTokenAuthenticator":
        """
        Create a WebTokenAuthenticator from a Zitadel service-account key file.

        Expected JSON format::

            {
                "type": "serviceaccount",
                "keyId": "<key-id>",
                "key": "<private-key>",
                "userId": "<user-id>"
            }

        :param host: Base URL for the API endpoints.
        :param json_path: File path to the key file.
        :return: A new instance of WebTokenAuthenticator.
        :raises ValueError: If the file cannot be read, is not a JSON object,
            lacks the string fields ``userId``, ``keyId`` and ``key``, or
            holds an invalid key.
        """
        try:
            with open(json_path, "r", encoding="utf-8") as file:
                content = file.read()
        except OSError as e:
            raise ValueError(f"Unable to read the key file at {json_path}") from e
        try:
            config = json.loads(content)
        except ValueError:
            config = None
        if not isinstance(config, dict):
            raise ValueError(f"The key file at {json_path} is not a JSON object")
        user_id = config.get("userId")
        key_id = config.get("keyId")
        private_key = config.get("key")
        if (
            not isinstance(user_id, str)
            or not isinstance(key_id, str)
            or not isinstance(private_key, str)
        ):
            raise ValueError(
                f"The key file at {json_path} must contain the string fields userId, keyId and key"
            )
        return cls.builder(host, user_id, private_key).key_id(key_id).build()

    @staticmethod
    def builder(
        host: str, user_id: str, private_key: str
    ) -> "WebTokenAuthenticatorBuilder":
        """
        Returns a builder for constructing a WebTokenAuthenticator.

        :param host: The base URL for the OAuth provider.
        :param user_id: The user ID, used as both the issuer and the subject.
        :param private_key: The PEM-encoded RSA private key used to sign the JWT.
        :return: A WebTokenAuthenticatorBuilder instance.
        :raises ValueError: If the host is not a valid http or https URL, the
            user ID is empty, or the key is not an RSA private key.
        """
        return WebTokenAuthenticatorBuilder(host, user_id, private_key)


class WebTokenAuthenticatorBuilder(
    OAuthAuthenticatorBuilder["WebTokenAuthenticatorBuilder"]
):
    """
    Builder for WebTokenAuthenticator.
    """

    def __init__(self, host: str, user_id: str, private_key: str):
        """
        Initializes the WebTokenAuthenticatorBuilder.

        :param host: The base URL for API endpoints.
        :param user_id: The user ID, used as both the issuer and the subject.
        :param private_key: The PEM-encoded RSA private key used to sign the JWT.
        """
        super().__init__(host)
        self.user_id = require_text(user_id, "User ID")
        self.private_key = _load_private_key(private_key)
        self.lifetime = timedelta(hours=1)
        self.algorithm = "RS256"
        self.kid: Optional[str] = None

    def token_lifetime_seconds(self, seconds: int) -> "WebTokenAuthenticatorBuilder":
        """
        Sets the JWT assertion lifetime in seconds.

        :param seconds: Lifetime of the JWT in seconds; must be positive.
        :return: The builder instance.
        :raises ValueError: If the lifetime is not positive.
        """
        if isinstance(seconds, bool) or not isinstance(seconds, int) or seconds <= 0:
            raise ValueError("Token lifetime must be a positive number of seconds.")
        self.lifetime = timedelta(seconds=seconds)
        return self

    def jwt_algorithm(self, jwt_algorithm: str) -> "WebTokenAuthenticatorBuilder":
        """
        Sets the JWT signing algorithm.

        :param jwt_algorithm: One of "RS256", "RS384" or "RS512".
        :return: The builder instance.
        :raises ValueError: If the algorithm is not supported.
        """
        if jwt_algorithm not in _ALGORITHMS:
            raise ValueError(
                f"Unsupported JWT algorithm '{jwt_algorithm}'; use RS256, RS384 or RS512."
            )
        self.algorithm = jwt_algorithm
        return self

    def key_id(self, key_id: str) -> "WebTokenAuthenticatorBuilder":
        """
        Sets the key ID sent as the ``kid`` header of the assertion.

        :param key_id: The key identifier.
        :return: The builder instance.
        :raises ValueError: If the key ID is empty.
        """
        self.kid = require_text(key_id, "Key ID")
        return self

    def build(self) -> WebTokenAuthenticator:
        """
        Builds and returns a new WebTokenAuthenticator instance.

        :return: A new WebTokenAuthenticator instance.
        """
        return WebTokenAuthenticator(
            open_id=self.open_id,
            scope=self.scope,
            jwt_issuer=self.user_id,
            jwt_subject=self.user_id,
            jwt_audience=self.open_id.get_host_endpoint(),
            private_key=self.private_key,
            jwt_lifetime=self.lifetime,
            jwt_algorithm=self.algorithm,
            key_id=self.kid,
        )
