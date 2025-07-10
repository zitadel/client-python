import logging
import multiprocessing
import platform
from typing import Optional, Union

from zitadel_client.auth.authenticator import Authenticator
from zitadel_client.version import Version


class Configuration:
    """This class contains various settings of the API client."""

    USER_AGENT = " ".join(
        [
            f"zitadel-client/{Version.VERSION}",
            "("
            + "; ".join(
                [
                    "lang=python",
                    f"lang_version={platform.python_version()}",
                    f"os={platform.system()}",
                    f"arch={platform.machine()}",
                ]
            )
            + ")",
        ]
    ).lower()

    def __init__(
        self,
        authenticator: Authenticator,
        ssl_ca_cert: Optional[str] = None,
        retries: Optional[int] = None,
        ca_cert_data: Optional[Union[str, bytes]] = None,
        *,
        debug: Optional[bool] = None,
    ) -> None:
        """Constructor"""
        self._user_agent = Configuration.USER_AGENT
        self.authenticator = authenticator
        self.refresh_api_key_hook = None
        self.logger = {
            "package_logger": logging.getLogger("zitadel_client"),
            "urllib3_logger": logging.getLogger("urllib3"),
        }
        self.logger_stream_handler = None
        self.verify_ssl = True
        self.ssl_ca_cert = ssl_ca_cert
        self.ca_cert_data = ca_cert_data
        self.cert_file = None
        self.key_file = None
        self.assert_hostname = None
        self.tls_server_name = None

        # noinspection PyUnresolvedReferences
        self.connection_pool_maxsize = multiprocessing.cpu_count() * 5
        """urllib3 connection pool's maximum number of connections saved
       per pool. urllib3 uses 1 connection as default value, but this is
       not the best value when you are making a lot of possibly parallel
       requests to the same host, which is often the case here.
       cpu_count * 5 is used as default value to increase performance.
    """

        self.safe_chars_for_path_param = ""
        self.retries = retries
        # Enable client side validation
        self.client_side_validation = True
        self.socket_options = None
        self.datetime_format = "%Y-%m-%dT%H:%M:%S.%f%z"
        self.date_format = "%Y-%m-%d"
        self._host = host
        self._access_token = access_token
        self._timeout = timeout
        self._connect_timeout = connect_timeout
        self._user_agent = user_agent

    @property
    def host(self) -> str:
        """Return generated host."""
        return self.authenticator.get_host()

    @property
    def user_agent(self) -> str:
        """
        Get the user agent string.

        Returns:
            str: The current value of the user agent.
        """
        return self._user_agent

    @user_agent.setter
    def user_agent(self, value: str) -> None:
        """
        Set the user agent string.

        Args:
            value (str): The new user agent string to set.
        """
        self._user_agent = value

    @property
    def access_token(self) -> str:
        """
        Gets the authentication access token (Bearer Token).
        """
        return self._access_token

    @property
    def timeout(self) -> int:
        """
        Gets the total request timeout in seconds.
        """
        return self._timeout

    @property
    def connect_timeout(self) -> int:
        """
        Gets the connection timeout in seconds.
        """
        return self._connect_timeout
