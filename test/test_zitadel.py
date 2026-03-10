import importlib
import inspect
import os
import pkgutil
import unittest
import urllib.request
from typing import Optional

from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.wait_strategies import PortWaitStrategy
from testcontainers.core.waiting_utils import wait_container_is_ready

from zitadel_client.auth.no_auth_authenticator import NoAuthAuthenticator
from zitadel_client.transport_options import TransportOptions
from zitadel_client.zitadel import Zitadel

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


@wait_container_is_ready()
def _wait_for_wiremock(host: str, port: str) -> None:
    url = f"http://{host}:{port}/__admin/mappings"
    with urllib.request.urlopen(url, timeout=5) as resp:  # noqa: S310
        if resp.status != 200:
            raise ConnectionError(f"WireMock not ready: {resp.status}")


class ZitadelServicesTest(unittest.TestCase):

    def test_services_dynamic(self) -> None:
        expected = set()
        package = importlib.import_module("zitadel_client.api")
        for _, modname, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
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
            and getattr(zitadel, attr).__class__.__module__.startswith("zitadel_client.api")
        }
        self.assertEqual(expected, actual)


class ZitadelTransportTest(unittest.TestCase):
    host: Optional[str] = None
    http_port: Optional[str] = None
    https_port: Optional[str] = None
    proxy_port: Optional[str] = None
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
            .with_volume_mapping(keystore_path, "/home/wiremock/keystore.p12", mode="ro")
            .with_volume_mapping(
                os.path.join(FIXTURES_DIR, "mappings"), "/home/wiremock/mappings", mode="ro"
            )
            .with_command(
                "--https-port 8443"
                " --https-keystore /home/wiremock/keystore.p12"
                " --keystore-password password"
                " --keystore-type PKCS12"
                " --global-response-templating"
            )
        )
        cls.wiremock.start()

        cls.proxy = (
            DockerContainer("ubuntu/squid:6.10-24.10_beta")
            .with_network(cls.network)
            .with_exposed_ports(3128)
            .with_volume_mapping(squid_conf, "/etc/squid/squid.conf", mode="ro")
            .waiting_for(PortWaitStrategy(3128))
        )
        cls.proxy.start()

        cls.host = cls.wiremock.get_container_host_ip()
        cls.http_port = cls.wiremock.get_exposed_port(8080)
        cls.https_port = cls.wiremock.get_exposed_port(8443)
        cls.proxy_port = cls.proxy.get_exposed_port(3128)

        _wait_for_wiremock(cls.host, cls.http_port)

    @classmethod
    def teardown_class(cls) -> None:
        if cls.proxy is not None:
            cls.proxy.stop()
        if cls.wiremock is not None:
            cls.wiremock.stop()
        if cls.network is not None:
            cls.network.remove()

    def test_custom_ca_cert(self) -> None:
        zitadel = Zitadel.with_client_credentials(
            f"https://{self.host}:{self.https_port}",
            "dummy-client",
            "dummy-secret",
            transport_options=TransportOptions(ca_cert_path=self.ca_cert_path),
        )
        response = zitadel.settings.get_general_settings({})
        self.assertEqual("https", response.default_language)

    def test_insecure_mode(self) -> None:
        zitadel = Zitadel.with_client_credentials(
            f"https://{self.host}:{self.https_port}",
            "dummy-client",
            "dummy-secret",
            transport_options=TransportOptions(insecure=True),
        )
        response = zitadel.settings.get_general_settings({})
        self.assertEqual("https", response.default_language)

    def test_default_headers(self) -> None:
        zitadel = Zitadel.with_client_credentials(
            f"http://{self.host}:{self.http_port}",
            "dummy-client",
            "dummy-secret",
            transport_options=TransportOptions(default_headers={"X-Custom-Header": "test-value"}),
        )
        response = zitadel.settings.get_general_settings({})
        self.assertEqual("http", response.default_language)
        self.assertEqual("test-value", response.default_org_id)

    def test_proxy_url(self) -> None:
        zitadel = Zitadel.with_access_token(
            "http://wiremock:8080",
            "test-token",
            transport_options=TransportOptions(proxy_url=f"http://{self.host}:{self.proxy_port}"),
        )
        response = zitadel.settings.get_general_settings({})
        self.assertEqual("http", response.default_language)

    def test_no_ca_cert_fails(self) -> None:
        with self.assertRaises(Exception):  # noqa: B017
            Zitadel.with_client_credentials(
                f"https://{self.host}:{self.https_port}",
                "dummy-client",
                "dummy-secret",
            )
