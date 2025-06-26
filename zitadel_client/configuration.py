import copy
import http.client as httplib
import logging
import multiprocessing
import platform
import sys
from logging import FileHandler
from typing import Any, Dict, Optional, Union

from typing_extensions import Self

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
        self.logger_format = "%(asctime)s %(levelname)s %(message)s"
        self.logger_stream_handler = None
        self.logger_file_handler: Optional[FileHandler] = None
        self.logger_file = None
        if debug is not None:
            self.debug = debug
        else:
            self.__debug = False
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

    def __deepcopy__(self, memo: Dict[int, Any]) -> Self:
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k not in ("logger", "logger_file_handler"):
                # noinspection PyArgumentList
                setattr(result, k, copy.deepcopy(v, memo))
        # shallow copy of loggers
        result.logger = copy.copy(self.logger)
        # use setters to configure loggers
        result.logger_file = self.logger_file
        result.debug = self.debug
        return result

    def __setattr__(self, name: str, value: Any) -> None:
        object.__setattr__(self, name, value)

    @property
    def logger_file(self) -> Optional[str]:
        """The logger file.

        If the logger_file is None, then add stream handler and remove file
        handler. Otherwise, add file handler and remove stream handler.

        :type: str
        """
        return self.__logger_file

    @logger_file.setter
    def logger_file(self, value: Optional[str]) -> None:
        """The logger file.

        If the logger_file is None, then add stream handler and remove file
        handler. Otherwise, add file handler and remove stream handler.

        :param value: The logger_file path.
        :type: str
        """
        self.__logger_file = value
        if self.__logger_file:
            # If set logging file,
            # then add file handler and remove stream handler.
            self.logger_file_handler = logging.FileHandler(self.__logger_file)
            self.logger_file_handler.setFormatter(self.logger_formatter)
            for _, logger in self.logger.items():
                logger.addHandler(self.logger_file_handler)

    @property
    def debug(self) -> bool:
        """Debug status

        :type: bool
        """
        return self.__debug

    @debug.setter
    def debug(self, value: bool) -> None:
        """Debug status

        :param value: The debug status, True or False.
        :type: bool
        """
        self.__debug = value
        if self.__debug:
            # if debug status is True, turn on debug logging
            for _, logger in self.logger.items():
                logger.setLevel(logging.DEBUG)
            # turn on httplib debug
            httplib.HTTPConnection.debuglevel = 1
        else:
            # if debug status is False, turn off debug logging,
            # setting log level to default `logging.WARNING`
            for _, logger in self.logger.items():
                logger.setLevel(logging.WARNING)
            # turn off httplib debug
            httplib.HTTPConnection.debuglevel = 0

    @property
    def logger_format(self) -> str:
        """The logger format.

        The logger_formatter will be updated when sets logger_format.

        :type: str
        """
        return self.__logger_format

    @logger_format.setter
    def logger_format(self, value: str) -> None:
        """The logger format.

        The logger_formatter will be updated when sets logger_format.

        :param value: The format string.
        :type: str
        """
        self.__logger_format = value
        self.logger_formatter = logging.Formatter(self.__logger_format)

    @staticmethod
    def to_debug_report() -> str:
        """Gets the essential information for debugging.

        :return: The report for debugging.
        """
        return (
            "Python SDK Debug Report:\n"
            "OS: {env}\n"
            "Python Version: {pyversion}\n"
            "Version of the API: 1.0.0\n"
            "SDK Package Version: 0.0.1".format(env=sys.platform, pyversion=sys.version)
        )

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
