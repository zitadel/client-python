import unittest

from testcontainers.core.container import DockerContainer


class OAuthAuthenticatorTest(unittest.TestCase):
    """
    Base test class for OAuth authenticators.

    This class starts a Docker container running the mock OAuth2 server
    (ghcr.io/navikt/mock-oauth2-server:2.1.10) before any tests run and stops it after all tests.
    It sets the class variable `oauth_host` to the container’s accessible URL.

    The container is configured to wait for an HTTP response from the "/" endpoint
    with a status code of 405, using HttpWaitStrategy.
    """

    oauth_host: str | None = None
    mock_oauth2_server: DockerContainer = None

    @classmethod
    def setup_class(cls) -> None:
        cls.mock_oauth2_server = DockerContainer("ghcr.io/navikt/mock-oauth2-server:2.1.10").with_exposed_ports(8080)
        cls.mock_oauth2_server.start()
        host = cls.mock_oauth2_server.get_container_host_ip()
        port = cls.mock_oauth2_server.get_exposed_port(8080)
        cls.oauth_host = f"http://{host}:{port}"

    @classmethod
    def teardown_class(cls) -> None:
        if cls.mock_oauth2_server is not None:
            cls.mock_oauth2_server.stop()
