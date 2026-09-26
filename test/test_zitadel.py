import importlib
import inspect
import os
import pkgutil
import socket
import time
import unittest
import urllib.request
from typing import Optional

from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.wait_strategies import PortWaitStrategy
from testcontainers.core.waiting_utils import wait_container_is_ready

from zitadel_client.auth.client_credentials_authenticator import (
    ClientCredentialsAuthenticator,
)
from zitadel_client.auth.no_auth_authenticator import NoAuthAuthenticator
from zitadel_client.auth.personal_access_token_authenticator import (
    PersonalAccessTokenAuthenticator,
)
from zitadel_client.errors import ApiException
from zitadel_client.errors.network_exception import NetworkException
from zitadel_client.transport_options import TransportOptions
from zitadel_client.zitadel import Zitadel

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


@wait_container_is_ready()
def _wait_for_wiremock(host: str, port: str) -> None:
    url = f"http://{host}:{port}/__admin/mappings"
    with urllib.request.urlopen(url, timeout=5) as resp:  # noqa: S310
        if resp.status != 200:
            raise ConnectionError(f"WireMock not ready: {resp.status}")


def _wait_for_ports(
    container: DockerContainer, ports: list[int], timeout: float = 60.0
) -> None:
    """Block until every given container port is both published by Docker and
    accepting TCP connections on the host.

    Both proxy ports must be reachable before their mapped ports are read: 3128
    is the open proxy and 3129 the same proxy gated by Basic credentials, and a
    single-port wait can return while 3129 is still unmapped.
    """
    host = container.get_container_host_ip()
    deadline = time.time() + timeout
    while True:
        try:
            for port in ports:
                mapped = container.get_exposed_port(port)
                if not mapped:
                    raise ConnectionError(f"port {port} not mapped yet")
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(2)
                    sock.connect((host, int(mapped)))
            return
        except (OSError, ValueError, TypeError):
            if time.time() > deadline:
                raise TimeoutError(
                    f"Proxy ports {ports} did not become available in time"
                )
            time.sleep(0.2)


class ZitadelServicesTest(unittest.TestCase):
    def test_services_dynamic(self) -> None:
        expected = set()
        package = importlib.import_module("zitadel_client.api")
        for _, modname, _ in pkgutil.walk_packages(
            package.__path__, package.__name__ + "."
        ):
            module = importlib.import_module(modname)
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ == modname and obj.__name__.endswith("ServiceApi"):
                    expected.add(obj)
        zitadel = Zitadel(NoAuthAuthenticator("http://dummy"))
        actual = {
            type(getattr(zitadel, attr))
            for attr in dir(zitadel)
            if not attr.startswith("_")
            and hasattr(getattr(zitadel, attr), "__class__")
            and getattr(zitadel, attr).__class__.__module__.startswith(
                "zitadel_client.api"
            )
        }
        self.assertEqual(expected, actual)


class ZitadelTransportTest(unittest.IsolatedAsyncioTestCase):
    host: Optional[str] = None
    http_port: Optional[str] = None
    https_port: Optional[str] = None
    proxy_port: Optional[str] = None
    proxy_auth_port: Optional[str] = None
    ca_cert_path: Optional[str] = None
    wiremock: DockerContainer = None
    proxy: DockerContainer = None
    network: Network = None

    @classmethod
    def setup_class(cls) -> None:
        cls.ca_cert_path = os.path.join(FIXTURES_DIR, "ca.pem")
        keystore_path = os.path.join(FIXTURES_DIR, "keystore.p12")
        squid_conf = os.path.join(FIXTURES_DIR, "squid.conf")

        cls.network = Network().create()

        cls.wiremock = (
            DockerContainer("wiremock/wiremock:3.12.1")
            .with_network(cls.network)
            .with_network_aliases("wiremock")
            .with_exposed_ports(8080, 8443)
            .with_volume_mapping(
                keystore_path, "/home/wiremock/keystore.p12", mode="ro"
            )
            .with_volume_mapping(
                os.path.join(FIXTURES_DIR, "mappings"),
                "/home/wiremock/mappings",
                mode="ro",
            )
            .with_command(
                "--https-port 8443 --https-keystore /home/wiremock/keystore.p12 --keystore-password password --keystore-type PKCS12 --global-response-templating"
            )
        )
        cls.wiremock.start()

        cls.proxy = (
            DockerContainer("ubuntu/squid:6.10-24.10_beta")
            .with_network(cls.network)
            .with_exposed_ports(3128, 3129)
            .with_volume_mapping(squid_conf, "/etc/squid/squid.conf", mode="ro")
            .waiting_for(PortWaitStrategy(3128))
        )
        cls.proxy.start()

        cls.host = cls.wiremock.get_container_host_ip()
        cls.http_port = cls.wiremock.get_exposed_port(8080)
        cls.https_port = cls.wiremock.get_exposed_port(8443)

        _wait_for_ports(cls.proxy, [3128, 3129])
        cls.proxy_port = cls.proxy.get_exposed_port(3128)
        cls.proxy_auth_port = cls.proxy.get_exposed_port(3129)

        _wait_for_wiremock(cls.host, cls.http_port)

    @classmethod
    def teardown_class(cls) -> None:
        if cls.proxy is not None:
            cls.proxy.stop()
        if cls.wiremock is not None:
            cls.wiremock.stop()
        if cls.network is not None:
            cls.network.remove()

    async def test_custom_ca_cert(self) -> None:
        transport = TransportOptions(ca_cert_path=self.ca_cert_path)
        zitadel = Zitadel.with_authenticator(
            ClientCredentialsAuthenticator.builder(
                f"https://{self.host}:{self.https_port}",
                "dummy-client",
                "dummy-secret",
            ).build(),
            transport_options=transport,
        )
        response = await zitadel.settings_service.get_general_settings({})
        self.assertEqual("https", response.default_language)

    async def test_insecure_mode(self) -> None:
        transport = TransportOptions(verify_ssl=False)
        zitadel = Zitadel.with_authenticator(
            ClientCredentialsAuthenticator.builder(
                f"https://{self.host}:{self.https_port}",
                "dummy-client",
                "dummy-secret",
            ).build(),
            transport_options=transport,
        )
        response = await zitadel.settings_service.get_general_settings({})
        self.assertEqual("https", response.default_language)

    async def test_default_headers(self) -> None:
        transport = TransportOptions(default_headers={"X-Custom-Header": "test-value"})
        zitadel = Zitadel.with_authenticator(
            ClientCredentialsAuthenticator.builder(
                f"http://{self.host}:{self.http_port}",
                "dummy-client",
                "dummy-secret",
            ).build(),
            transport_options=transport,
        )
        response = await zitadel.settings_service.get_general_settings({})
        self.assertEqual("http", response.default_language)
        self.assertEqual("test-value", response.default_org_id)

    async def test_proxy_url(self) -> None:
        zitadel = Zitadel.with_authenticator(
            PersonalAccessTokenAuthenticator(
                "http://wiremock:8080",
                "test-token",
            ),
            transport_options=TransportOptions(
                proxy=f"http://{self.host}:{self.proxy_port}"
            ),
        )
        response = await zitadel.settings_service.get_general_settings({})
        self.assertEqual("http", response.default_language)

    async def test_proxy_requires_credentials(self) -> None:
        zitadel = Zitadel.with_authenticator(
            PersonalAccessTokenAuthenticator(
                "http://wiremock:8080",
                "test-token",
            ),
            transport_options=TransportOptions(
                proxy=f"http://{self.host}:{self.proxy_auth_port}"
            ),
        )
        with self.assertRaises(ApiException) as context:
            await zitadel.settings_service.get_general_settings({})
        self.assertEqual(407, context.exception.status_code)

    async def test_proxy_with_credentials(self) -> None:
        zitadel = Zitadel.with_authenticator(
            PersonalAccessTokenAuthenticator(
                "http://wiremock:8080",
                "test-token",
            ),
            transport_options=TransportOptions(
                proxy=f"http://user:pass@{self.host}:{self.proxy_auth_port}"
            ),
        )
        response = await zitadel.settings_service.get_general_settings({})
        self.assertEqual("http", response.default_language)

    async def test_no_ca_cert_fails(self) -> None:
        zitadel = Zitadel.with_authenticator(
            ClientCredentialsAuthenticator.builder(
                f"https://{self.host}:{self.https_port}",
                "dummy-client",
                "dummy-secret",
            ).build()
        )
        with self.assertRaises(NetworkException) as context:
            await zitadel.settings_service.get_general_settings({})
        self.assertIs(NetworkException, type(context.exception))
