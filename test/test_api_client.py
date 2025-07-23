import json
import time
import unittest
import urllib
import urllib.request

from testcontainers.core.container import DockerContainer

from zitadel_client import ApiClient, Configuration
from zitadel_client.auth.personal_access_token_authenticator import (
    PersonalAccessTokenAuthenticator,
)


class TestApiClient(unittest.TestCase):
    """
    Test case for interacting with the WireMock mock OAuth2 server.
    """

    mock_oauth2_server: DockerContainer
    oauth_host: str

    @classmethod
    def setup_class(cls) -> None:
        """
        Starts the WireMock Docker container and exposes the required port.
        Sets up the OAuth server URL.
        """
        cls.mock_oauth2_server = DockerContainer("wiremock/wiremock:3.12.1").with_exposed_ports(8080)
        cls.mock_oauth2_server.start()

        host = cls.mock_oauth2_server.get_container_host_ip()
        port = cls.mock_oauth2_server.get_exposed_port(8080)
        # noinspection HttpUrlsUsage
        cls.oauth_host = f"http://{host}:{port}"

    @classmethod
    def teardown_class(cls) -> None:
        """
        Stops the WireMock Docker container.
        """
        if cls.mock_oauth2_server is not None:
            cls.mock_oauth2_server.stop()

    def test_assert_headers_and_content_type(self) -> None:
        """
        Test the behavior of API client when sending requests to the mock OAuth2 server,
        asserting headers and content type.
        """
        time.sleep(20)

        with urllib.request.urlopen(  # noqa S310 allow all URL schemes
            urllib.request.Request(  # noqa S310 allow all URL schemes
                self.oauth_host + "/__admin/mappings",
                data=json.dumps(
                    {
                        "request": {
                            "method": "GET",
                            "url": "/your/endpoint",
                            "headers": {
                                "Authorization": {"equalTo": "Bearer mm"},
                                "User-Agent": {
                                    "matches": "^zitadel-client/\\d+\\.\\d+\\.\\d+(-[a-zA-Z0-9]+(\\.\\d+)?)? \\(lang=python; lang_version=[^;]+; os=[^;]+; arch=[^;]+\\)$"  # noqa E501
                                },
                            },
                        },
                        "response": {
                            "status": 200,
                            "body": '{"key": "value"}',
                            "headers": {"Content-Type": "application/json"},
                        },
                    }
                ).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
        ) as response:
            response.read().decode()

        api_client = ApiClient(Configuration(authenticator=PersonalAccessTokenAuthenticator(self.oauth_host, "mm")))

        api_response = api_client.call_api(
            *(
                api_client.param_serialize(
                    method="GET",
                    resource_path="/your/endpoint",
                )
            )
        )

        if api_response.status != 200:
            self.fail(f"Expected status 200, but got {api_response.status}")


if __name__ == "__main__":
    unittest.main()
