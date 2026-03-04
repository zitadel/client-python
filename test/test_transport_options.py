import json
import os
import ssl
import tempfile
import time
import unittest
import urllib.request
from typing import Optional

from testcontainers.core.container import DockerContainer

from zitadel_client.transport_options import TransportOptions
from zitadel_client.zitadel import Zitadel


class TransportOptionsTest(unittest.TestCase):
    """
    Test class for verifying transport options (default_headers, ca_cert_path, insecure)
    on the Zitadel factory methods.

    This class starts a Docker container running WireMock with HTTPS support before any
    tests run and stops it after all tests. It registers stubs for OpenID Configuration
    discovery and the token endpoint so that Zitadel.with_client_credentials() can
    complete its initialization flow.
    """

    host: Optional[str] = None
    http_port: Optional[str] = None
    https_port: Optional[str] = None
    ca_cert_path: Optional[str] = None
    wiremock: DockerContainer = None

    @classmethod
    def setup_class(cls) -> None:
        cls.wiremock = (
            DockerContainer("wiremock/wiremock:3.3.1")
            .with_exposed_ports(8080, 8443)
            .with_command("--https-port 8443 --global-response-templating")
        )
        cls.wiremock.start()

        cls.host = cls.wiremock.get_container_host_ip()
        cls.http_port = cls.wiremock.get_exposed_port(8080)
        cls.https_port = cls.wiremock.get_exposed_port(8443)

        # Wait for WireMock to be ready by polling the admin API
        admin_url = f"http://{cls.host}:{cls.http_port}/__admin/mappings"
        for _ in range(30):
            try:
                with urllib.request.urlopen(admin_url, timeout=2) as resp:  # noqa: S310
                    if resp.status == 200:
                        break
            except Exception:  # noqa: S110, BLE001
                pass
            time.sleep(1)

        # Register stub for OpenID Configuration discovery
        oidc_stub = json.dumps(
            {
                "request": {"method": "GET", "url": "/.well-known/openid-configuration"},
                "response": {
                    "status": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": (
                        '{"issuer":"{{request.baseUrl}}",'
                        '"token_endpoint":"{{request.baseUrl}}/oauth/v2/token",'
                        '"authorization_endpoint":"{{request.baseUrl}}/oauth/v2/authorize",'
                        '"userinfo_endpoint":"{{request.baseUrl}}/oidc/v1/userinfo",'
                        '"jwks_uri":"{{request.baseUrl}}/oauth/v2/keys"}'
                    ),
                },
            }
        ).encode()

        req = urllib.request.Request(
            f"http://{cls.host}:{cls.http_port}/__admin/mappings",
            data=oidc_stub,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:  # noqa: S310
            assert resp.status == 201

        # Register stub for the token endpoint
        token_stub = json.dumps(
            {
                "request": {"method": "POST", "url": "/oauth/v2/token"},
                "response": {
                    "status": 200,
                    "headers": {"Content-Type": "application/json"},
                    "jsonBody": {
                        "access_token": "test-token-12345",
                        "token_type": "Bearer",
                        "expires_in": 3600,
                    },
                },
            }
        ).encode()

        req = urllib.request.Request(
            f"http://{cls.host}:{cls.http_port}/__admin/mappings",
            data=token_stub,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:  # noqa: S310
            assert resp.status == 201

        # Extract the WireMock HTTPS certificate to a temp file
        pem_cert = ssl.get_server_certificate((cls.host, int(cls.https_port)))
        cert_file = tempfile.NamedTemporaryFile(suffix=".pem", delete=False)
        cert_file.write(pem_cert.encode())
        cert_file.close()
        cls.ca_cert_path = cert_file.name

    @classmethod
    def teardown_class(cls) -> None:
        if cls.ca_cert_path is not None:
            os.unlink(cls.ca_cert_path)
        if cls.wiremock is not None:
            cls.wiremock.stop()

    def test_custom_ca_cert(self) -> None:
        zitadel = Zitadel.with_client_credentials(
            f"https://{self.host}:{self.https_port}",
            "dummy-client",
            "dummy-secret",
            ca_cert_path=self.ca_cert_path,
        )
        self.assertIsNotNone(zitadel)

    def test_insecure_mode(self) -> None:
        zitadel = Zitadel.with_client_credentials(
            f"https://{self.host}:{self.https_port}",
            "dummy-client",
            "dummy-secret",
            insecure=True,
        )
        self.assertIsNotNone(zitadel)

    def test_default_headers(self) -> None:
        # Use HTTP to avoid TLS concerns
        zitadel = Zitadel.with_client_credentials(
            f"http://{self.host}:{self.http_port}",
            "dummy-client",
            "dummy-secret",
            default_headers={"X-Custom-Header": "test-value"},
        )
        self.assertIsNotNone(zitadel)

        # Verify via WireMock request journal
        journal_url = f"http://{self.host}:{self.http_port}/__admin/requests"
        with urllib.request.urlopen(journal_url) as response:  # noqa: S310
            journal = json.loads(response.read().decode())

        found_header = False
        for req in journal.get("requests", []):
            headers = req.get("request", {}).get("headers", {})
            if "X-Custom-Header" in headers:
                found_header = True
                break
        self.assertTrue(found_header, "Custom header should be present in WireMock request journal")

    def test_proxy_url(self) -> None:
        # Use HTTP (not HTTPS) to avoid TLS complications with the proxy
        zitadel = Zitadel.with_client_credentials(
            f"http://{self.host}:{self.http_port}",
            "dummy-client",
            "dummy-secret",
            proxy_url=f"http://{self.host}:{self.http_port}",
        )
        self.assertIsNotNone(zitadel)

    def test_no_ca_cert_fails(self) -> None:
        with self.assertRaises(Exception):  # noqa: B017
            Zitadel.with_client_credentials(
                f"https://{self.host}:{self.https_port}",
                "dummy-client",
                "dummy-secret",
            )

    def test_transport_options_object(self) -> None:
        opts = TransportOptions(insecure=True)
        zitadel = Zitadel.with_client_credentials(
            f"https://{self.host}:{self.https_port}",
            "dummy-client",
            "dummy-secret",
            transport_options=opts,
        )
        self.assertIsNotNone(zitadel)
