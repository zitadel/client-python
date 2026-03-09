import json
import ssl
import urllib.error
import urllib.request
from typing import Optional
from urllib.parse import urljoin

from zitadel_client.transport_options import TransportOptions


class OpenId:
    """
    OpenId retrieves OpenID Connect configuration from a given host.

    It builds the well-known configuration URL from the provided hostname,
    fetches the configuration, and extracts the token endpoint.
    """

    host_endpoint: str
    token_endpoint: str

    def __init__(  # noqa: C901
        self,
        hostname: str,
        transport_options: Optional[TransportOptions] = None,
    ):
        """
        Initialize the OpenId configuration fetcher.

        :param hostname: The Zitadel instance hostname or URL.
        :param transport_options: Optional transport options for TLS, proxy, and headers.
        """
        if transport_options is None:
            transport_options = TransportOptions.defaults()

        # noinspection HttpUrlsUsage
        if not (hostname.startswith("http://") or hostname.startswith("https://")):
            hostname = "https://" + hostname

        self.host_endpoint = hostname
        well_known_url = self.build_well_known_url(hostname)

        try:
            # noinspection HttpUrlsUsage
            if not well_known_url.lower().startswith(("http://", "https://")):
                raise ValueError("Invalid URL scheme. Only 'http' and 'https' are allowed.")

            request = urllib.request.Request(well_known_url)  # noqa: S310
            if transport_options.default_headers:
                for header_name, header_value in transport_options.default_headers.items():
                    request.add_header(header_name, header_value)

            if transport_options.insecure:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            elif transport_options.ca_cert_path:
                ctx = ssl.create_default_context()
                ctx.check_hostname = True
                ctx.verify_mode = ssl.CERT_REQUIRED
                ctx.load_verify_locations(transport_options.ca_cert_path)
            else:
                ctx = None

            if transport_options.proxy_url:
                proxy_handler = urllib.request.ProxyHandler(
                    {"http": transport_options.proxy_url, "https": transport_options.proxy_url}
                )
                if ctx:
                    https_handler = urllib.request.HTTPSHandler(context=ctx)
                    opener = urllib.request.build_opener(proxy_handler, https_handler)
                else:
                    opener = urllib.request.build_opener(proxy_handler)
                response_ctx = opener.open(request)
            else:
                response_ctx = urllib.request.urlopen(request, context=ctx)  # noqa: S310

            with response_ctx as response:
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
