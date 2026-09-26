from typing import Any, Dict, List, Optional
from unittest.mock import Mock

from test.auth.test_oauth_authenticator import OAuthAuthenticatorTest
from zitadel_client.api_http_response import ApiHttpResponse
from zitadel_client.auth.client_credentials_authenticator import (
    ClientCredentialsAuthenticator,
)
from zitadel_client.auth.open_id import OpenId
from zitadel_client.default_api_client import DefaultApiClient
from zitadel_client.errors import (
    ApiException,
    SerializationException,
    ZitadelException,
)
from zitadel_client.errors.internal_server_error_exception import (
    InternalServerErrorException,
)
from zitadel_client.errors.network_exception import NetworkException
from zitadel_client.errors.not_found_exception import NotFoundException
from zitadel_client.errors.oauth2_server_exception import OAuth2ServerException
from zitadel_client.errors.oauth2_token_exception import OAuth2TokenException
from zitadel_client.transport_options import TransportOptions

HOST = "https://zitadel.example.com"
DISCOVERY = '{"issuer":"' + HOST + '","token_endpoint":"' + HOST + '/oauth/v2/token"}'


class StubApiClient:
    """An ApiClient that records token requests and answers with canned responses."""

    def __init__(self, discovery: ApiHttpResponse, token: ApiHttpResponse) -> None:
        self.discovery = discovery
        self.token = token
        self.bodies: List[str] = []

    def send_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        body: Any = None,
        no_redirect: bool = False,
    ) -> ApiHttpResponse:
        if url.endswith("/.well-known/openid-configuration"):
            return self.discovery
        self.bodies.append(str(body))
        return self.token


def response(status: int, body: str) -> ApiHttpResponse:
    return ApiHttpResponse(status, body, {})


def authenticator(
    api_client: Any, host: Optional[str] = None
) -> ClientCredentialsAuthenticator:
    auth = ClientCredentialsAuthenticator.builder(
        host or HOST, "client-1", "client-secret"
    ).build()
    auth.set_api_client(api_client)
    return auth


def token_authenticator(status: int, body: str) -> ClientCredentialsAuthenticator:
    return authenticator(
        StubApiClient(response(200, DISCOVERY), response(status, body))
    )


class ClientCredentialsAuthenticatorTest(OAuthAuthenticatorTest):
    """
    Tests for ClientCredentialsAuthenticator and the OAuth contract it shares
    with every OAuth authenticator: host validation, OpenID discovery failures
    and token endpoint failures.

    No contract test reaches a real host. HTTP-level cases use an in-memory
    ApiClient that answers with canned responses; the transport case uses the
    real DefaultApiClient against a local port nothing listens on.
    """

    def test_redacts_secret_in_repr(self) -> None:
        """The client secret is masked in repr while the client id stays visible."""
        secret = "super-secret-value-9000"
        open_id = Mock(spec=OpenId)
        open_id.get_host_endpoint.return_value = "https://example.zitadel.cloud"
        auth = ClientCredentialsAuthenticator(open_id, "client-1", secret, "openid")

        rendered = repr(auth)

        self.assertNotIn(secret, rendered)
        self.assertIn("***", rendered)
        self.assertIn("client-1", rendered)

    # noinspection DuplicatedCode
    def test_refresh_token(self) -> None:
        assert self.oauth_host is not None
        auth = self.inject_api_client(
            ClientCredentialsAuthenticator.builder(
                self.oauth_host, "dummy-client", "dummy-secret"
            )
            .scopes("openid", "foo")
            .build()
        )

        self.assertTrue(auth.get_auth_token(), "Access token should not be empty")
        token = auth.refresh_token()
        self.assertEqual({"Authorization": "Bearer " + token}, auth.get_auth_headers())
        self.assertTrue(token, "Access token should not be null")
        self.assertEqual(token, auth.get_auth_token())
        self.assertEqual(self.oauth_host, auth.get_host())
        self.assertNotEqual(
            auth.refresh_token(),
            auth.refresh_token(),
            "Two refreshToken calls should produce different tokens",
        )

    def test_mints_and_caches_token(self) -> None:
        api_client = StubApiClient(
            response(200, DISCOVERY),
            response(200, '{"access_token":"t0k3n","expires_in":3600}'),
        )
        auth = authenticator(api_client)

        self.assertEqual("t0k3n", auth.get_auth_token())
        self.assertEqual({"Authorization": "Bearer t0k3n"}, auth.get_auth_headers())
        self.assertEqual(1, len(api_client.bodies))
        self.assertTrue(
            api_client.bodies[0].startswith(
                "grant_type=client_credentials&scope=openid"
            )
        )

    def test_rejects_empty_credentials(self) -> None:
        with self.assertRaises(ValueError):
            ClientCredentialsAuthenticator.builder(HOST, "", "client-secret")
        with self.assertRaises(ValueError):
            ClientCredentialsAuthenticator.builder(HOST, "client-1", " ")

    def test_rejects_bad_host(self) -> None:
        for host in ("", "ftp://example.com", "https://"):
            with self.assertRaises(ValueError) as context:
                ClientCredentialsAuthenticator.builder(
                    host, "client-1", "client-secret"
                )
            self.assertIs(ValueError, type(context.exception))
            self.assertNotIsInstance(context.exception, ZitadelException)

    def test_requires_api_client(self) -> None:
        auth = ClientCredentialsAuthenticator.builder(
            HOST, "client-1", "client-secret"
        ).build()

        with self.assertRaises(RuntimeError) as context:
            auth.get_auth_token()
        self.assertIs(RuntimeError, type(context.exception))

    def test_discovery_unreachable(self) -> None:
        auth = authenticator(
            DefaultApiClient(TransportOptions()), host="http://127.0.0.1:1"
        )

        with self.assertRaises(NetworkException) as context:
            auth.get_auth_token()
        self.assertIs(NetworkException, type(context.exception))
        self.assertIsInstance(context.exception, ApiException)
        self.assertEqual(0, context.exception.status_code)

    def test_discovery_non_2xx(self) -> None:
        with self.assertRaises(NotFoundException) as context:
            authenticator(
                StubApiClient(response(404, "{}"), response(200, "{}"))
            ).get_auth_token()
        self.assertIs(NotFoundException, type(context.exception))
        self.assertEqual(404, context.exception.status_code)
        self.assertIsInstance(context.exception, ZitadelException)

        with self.assertRaises(InternalServerErrorException) as server:
            authenticator(
                StubApiClient(response(500, "{}"), response(200, "{}"))
            ).get_auth_token()
        self.assertIs(InternalServerErrorException, type(server.exception))

    def test_discovery_malformed(self) -> None:
        for body in ("not json", "[]", '{"issuer":"x"}'):
            with self.assertRaises(SerializationException) as context:
                authenticator(
                    StubApiClient(response(200, body), response(200, "{}"))
                ).get_auth_token()
            self.assertIs(SerializationException, type(context.exception))
            self.assertIsInstance(context.exception, ZitadelException)

    def test_token_endpoint_rejects(self) -> None:
        with self.assertRaises(OAuth2ServerException) as context:
            token_authenticator(
                401, '{"error":"invalid_client","error_description":"bad"}'
            ).get_auth_token()
        self.assertIs(OAuth2ServerException, type(context.exception))
        self.assertEqual(401, context.exception.status_code)
        self.assertEqual("invalid_client", context.exception.code)
        self.assertEqual("bad", context.exception.description)
        self.assertIsInstance(context.exception, ZitadelException)
        self.assertNotIsInstance(context.exception, ApiException)

        with self.assertRaises(OAuth2ServerException) as raw:
            token_authenticator(503, "down").get_auth_token()
        self.assertEqual(503, raw.exception.status_code)
        self.assertEqual("down", raw.exception.raw_body)

    def test_token_endpoint_unusable(self) -> None:
        for body in ('{"token_type":"Bearer"}', "not json", '{"access_token":""}'):
            with self.assertRaises(OAuth2TokenException) as context:
                token_authenticator(200, body).get_auth_token()
            self.assertIs(OAuth2TokenException, type(context.exception))
            self.assertIsInstance(context.exception, ZitadelException)

    def test_rejects_bad_scopes(self) -> None:
        builder = ClientCredentialsAuthenticator.builder(
            HOST, "client-1", "client-secret"
        )

        for scopes in ((), ("open id",), ("",)):
            with self.assertRaises(ValueError) as context:
                builder.scopes(*scopes)
            self.assertIs(ValueError, type(context.exception))

    def test_joins_scopes(self) -> None:
        api_client = StubApiClient(
            response(200, DISCOVERY), response(200, '{"access_token":"t"}')
        )
        auth = (
            ClientCredentialsAuthenticator.builder(HOST, "client-1", "client-secret")
            .scopes("openid", "profile", "openid")
            .build()
        )
        auth.set_api_client(api_client)

        auth.get_auth_token()

        self.assertIn("&scope=openid+profile&", api_client.bodies[0])
