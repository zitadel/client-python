import json
import urllib
import urllib.error
import urllib.request
from urllib.parse import urljoin


class OpenId:
    """
    OpenId retrieves OpenID Connect configuration from a given host.

    It builds the well-known configuration URL from the provided hostname,
    fetches the configuration, and extracts the token endpoint.
    """

    host_endpoint: str
    token_endpoint: str

    def __init__(self, hostname: str):
        # noinspection HttpUrlsUsage
        if not (hostname.startswith("http://") or hostname.startswith("https://")):
            hostname = "https://" + hostname

        self.host_endpoint = hostname
        well_known_url = self.build_well_known_url(hostname)

        try:
            # noinspection HttpUrlsUsage
            if not well_known_url.lower().startswith(("http://", "https://")):
                raise ValueError("Invalid URL scheme. Only 'http' and 'https' are allowed.")

            with urllib.request.urlopen(well_known_url) as response:  # noqa S310
                if response.status != 200:
                    raise Exception(f"Failed to fetch OpenID configuration: HTTP {response.status}")
                config = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as e:
            raise Exception(f"URL error occurred: {e}") from e
        except json.JSONDecodeError as e:
            raise Exception("Failed to decode JSON response") from e

        token_endpoint = config.get("token_endpoint")
        if not token_endpoint:
            raise Exception("token_endpoint not found in OpenID configuration")

        self.token_endpoint = token_endpoint

    @staticmethod
    def build_well_known_url(hostname: str) -> str:
        """
        Builds the well-known OpenID configuration URL for the given hostname.
        """
        return urljoin(hostname, "/.well-known/openid-configuration")

    def get_host_endpoint(self) -> str:
        """
        Returns the host endpoint URL.
        """
        return self.host_endpoint

    def get_token_endpoint(self) -> str:
        """
        Returns the token endpoint URL extracted from the OpenID configuration.
        """
        return self.token_endpoint
