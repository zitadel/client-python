import json
import os
import tempfile
from unittest.mock import Mock

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)

from test.auth.test_oauth_authenticator import OAuthAuthenticatorTest
from zitadel_client.auth.open_id import OpenId
from zitadel_client.auth.web_token_authenticator import WebTokenAuthenticator


class WebTokenAuthenticatorTest(OAuthAuthenticatorTest):
    """
    Test for WebTokenAuthenticator to verify JWT token refresh functionality using the builder.
    """

    def test_redacts_secret_in_repr(self) -> None:
        """The private key and cached access token are masked in repr.

        Uses a mocked OpenId so no network call is made; the cached token is
        seeded directly to exercise the masked representation.
        """
        token = "minted-access-token-do-not-leak"
        private_key = "-----BEGIN PRIVATE KEY-----secret-key-material-----END-----"
        open_id = Mock(spec=OpenId)
        open_id.get_host_endpoint.return_value = "https://example.zitadel.cloud"
        authenticator = WebTokenAuthenticator(
            open_id,
            "openid",
            "issuer",
            "subject",
            "audience",
            private_key,
        )
        authenticator._access_token = token

        rendered = repr(authenticator)

        self.assertNotIn(token, rendered)
        self.assertNotIn(private_key, rendered)
        self.assertIn("***", rendered)

    # noinspection DuplicatedCode
    def test_refresh_token_using_builder(self) -> None:

        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        private_key_pem = key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption(),
        ).decode("utf-8")

        assert self.oauth_host is not None
        authenticator = self.inject_api_client(
            WebTokenAuthenticator.builder(
                self.oauth_host, "dummy-client", private_key_pem
            )
            .token_lifetime_seconds(3600)
            .build()
        )

        self.assertTrue(
            authenticator.get_auth_token(), "Access token should not be empty"
        )
        token = authenticator.refresh_token()
        self.assertEqual(
            {"Authorization": "Bearer " + token},
            authenticator.get_auth_headers(),
        )
        self.assertTrue(token, "Access token should not be null")
        self.assertEqual(token, authenticator.get_auth_token())
        self.assertEqual(self.oauth_host, authenticator.get_host())
        self.assertNotEqual(
            authenticator.refresh_token(),
            authenticator.refresh_token(),
            "Two refreshToken calls should produce different tokens",
        )

    @staticmethod
    def _pem() -> str:
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        return key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption(),
        ).decode("utf-8")

    def _key_file(self, content: str) -> str:
        handle, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(handle, "w", encoding="utf-8") as file:
            file.write(content)
        self.addCleanup(os.remove, path)
        return path

    def test_loads_key_file(self) -> None:
        """A Zitadel key file builds an authenticator for the host."""
        path = self._key_file(
            json.dumps(
                {
                    "type": "serviceaccount",
                    "keyId": "key-1",
                    "userId": "user-1",
                    "key": self._pem(),
                }
            )
        )

        auth = WebTokenAuthenticator.from_json("https://example.zitadel.cloud", path)

        self.assertEqual("https://example.zitadel.cloud", auth.get_host())

    def test_rejects_bad_key_file(self) -> None:
        """A missing or malformed key file is a ValueError."""
        host = "https://example.zitadel.cloud"
        with self.assertRaises(ValueError) as missing:
            WebTokenAuthenticator.from_json(
                host, os.path.join(tempfile.gettempdir(), "absent-zitadel-key.json")
            )
        self.assertIs(ValueError, type(missing.exception))

        for content in (
            "not json",
            "[]",
            '{"userId":"user-1","keyId":"key-1"}',
            '{"userId":"user-1","keyId":"key-1","key":"not a pem"}',
        ):
            path = self._key_file(content)
            with self.assertRaises(ValueError) as context:
                WebTokenAuthenticator.from_json(host, path)
            self.assertIs(ValueError, type(context.exception))

    def test_rejects_bad_builder_arguments(self) -> None:
        """Invalid builder arguments are a ValueError."""
        host = "https://example.zitadel.cloud"
        pem = self._pem()
        builder = WebTokenAuthenticator.builder(host, "user-1", pem)

        for action in (
            lambda: WebTokenAuthenticator.builder(host, "", pem),
            lambda: WebTokenAuthenticator.builder(host, "user-1", "not a pem"),
            lambda: builder.jwt_algorithm("HS256"),
            lambda: builder.token_lifetime_seconds(0),
            lambda: builder.key_id(""),
        ):
            with self.assertRaises(ValueError) as context:
                action()
            self.assertIs(ValueError, type(context.exception))
