import time
import unittest
import urllib.error
import urllib.request
from typing import Optional, TypeVar
from unittest.mock import Mock

from testcontainers.core.container import DockerContainer

from zitadel_client.auth.client_credentials_authenticator import (
    ClientCredentialsAuthenticator,
)
from zitadel_client.auth.oauth_authenticator import OAuthAuthenticator
from zitadel_client.auth.open_id import OpenId
from zitadel_client.default_api_client import DefaultApiClient
from zitadel_client.transport_options import TransportOptions

A = TypeVar("A", bound=OAuthAuthenticator)


class OAuthAuthenticatorTest(unittest.TestCase):
    """
    Base test class for OAuth authenticators.

    This class starts a Docker container running the mock OAuth2 server
    (ghcr.io/navikt/mock-oauth2-server:2.1.10) before any tests run and stops it after all tests.
    It sets the class variable `oauth_host` to the container’s accessible URL.

    The container is configured to wait for an HTTP response from the "/" endpoint
    with a status code of 405, using HttpWaitStrategy.
    """

    oauth_host: Optional[str] = None
    mock_oauth2_server: DockerContainer = None

    @classmethod
    def setup_class(cls) -> None:
        cls.mock_oauth2_server = DockerContainer(
            "ghcr.io/navikt/mock-oauth2-server:2.1.10"
        ).with_exposed_ports(8080)
        cls.mock_oauth2_server.start()
        host = cls.mock_oauth2_server.get_container_host_ip()
        port = cls.mock_oauth2_server.get_exposed_port(8080)
        # noinspection HttpUrlsUsage
        cls.oauth_host = f"http://{host}:{port}"
        # Wait for HTTP GET / -> 405 (mock-oauth2-server ready), the same
        # readiness strategy the other SDK test harnesses use — no fixed sleep.
        deadline = time.time() + 30
        while True:
            try:
                urllib.request.urlopen(cls.oauth_host + "/", timeout=1)
            except urllib.error.HTTPError as exc:
                if exc.code == 405:
                    break
            except Exception:
                pass
            if time.time() >= deadline:
                raise RuntimeError(
                    f"mock-oauth2-server not ready at {cls.oauth_host} within 30s"
                )
            time.sleep(0.5)

    @classmethod
    def teardown_class(cls) -> None:
        if cls.mock_oauth2_server is not None:
            cls.mock_oauth2_server.stop()

    def test_redacts_secret_in_repr(self) -> None:
        """The cached/minted access token is masked in repr.

        Uses a concrete OAuth authenticator with a mocked OpenId so no network
        call is made; the cached token is seeded directly.
        """
        token = "minted-access-token-do-not-leak"
        open_id = Mock(spec=OpenId)
        open_id.get_host_endpoint.return_value = "https://example.zitadel.cloud"
        authenticator = ClientCredentialsAuthenticator(
            open_id, "client-1", "client-secret", {"openid"}
        )
        authenticator._access_token = token

        rendered = OAuthAuthenticator.__repr__(authenticator)

        self.assertNotIn(token, rendered)
        self.assertIn("***", rendered)

    @staticmethod
    def inject_api_client(authenticator: A) -> A:
        """
        Inject a real transport into an OAuth authenticator.

        OAuth authenticators require a transport to perform token exchange. The
        real client wires this via ``set_api_client`` (see
        ``Zitadel.__init__``); mirror that here so the bespoke tests can exchange
        tokens against the mock OAuth2 server. The mock server is plain HTTP, so
        default transport options are fine.
        """
        authenticator.set_api_client(DefaultApiClient(TransportOptions()))
        return authenticator
