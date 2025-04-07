import json
from urllib.parse import urljoin

import urllib3


class OpenId:
  """
  OpenId retrieves OpenID Connect configuration from a given host.

  It builds the well-known configuration URL from the provided hostname,
  fetches the configuration, and extracts the token endpoint.
  """

  def __init__(self, hostname: str):
    if not (hostname.startswith("http://") or hostname.startswith("https://")):
      hostname = "https://" + hostname  # Default to HTTPS if no scheme is provided.
    self.host_endpoint = hostname
    well_known_url = self.build_well_known_url(hostname)

    http = urllib3.PoolManager()
    response = http.request("GET", well_known_url)

    if response.status != 200:
      raise Exception(f"Failed to fetch OpenID configuration: HTTP {response.status}")

    # Decode and load the JSON response
    config = json.loads(response.data.decode('utf-8'))
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
