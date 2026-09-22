import json
import threading
from typing import Dict, Optional
from urllib.parse import urlsplit

from zitadel_client.api_client import ApiClient
from zitadel_client.errors import ApiException
from zitadel_client.errors.bad_request_exception import BadRequestException
from zitadel_client.errors.client_exception import ClientException
from zitadel_client.errors.conflict_exception import ConflictException
from zitadel_client.errors.forbidden_exception import ForbiddenException
from zitadel_client.errors.internal_server_error_exception import (
    InternalServerErrorException,
)
from zitadel_client.errors.not_found_exception import NotFoundException
from zitadel_client.errors.server_exception import ServerException
from zitadel_client.errors.unauthorized_exception import UnauthorizedException
from zitadel_client.errors.unprocessable_entity_exception import (
    UnprocessableEntityException,
)
from zitadel_client.object_serializer import SerializationException

_WELL_KNOWN_PATH = "/.well-known/openid-configuration"

_STATUS_EXCEPTIONS = {
    400: BadRequestException,
    401: UnauthorizedException,
    403: ForbiddenException,
    404: NotFoundException,
    409: ConflictException,
    422: UnprocessableEntityException,
    500: InternalServerErrorException,
}


class OpenId:
    """
    Resolves the OpenID Connect discovery document for a Zitadel host.

    The constructor only validates and normalises the host; it performs no
    I/O. The ``token_endpoint`` is fetched through the shared
    :class:`ApiClient` the first time :meth:`get_token_endpoint` is called, so
    discovery honours the SDK's proxy, TLS and timeout settings and fails with
    the same error types as any other request:

    - no HTTP response: :class:`NetworkException` or
      :class:`NetworkTimeoutException`;
    - a non-2xx status: the :class:`ApiException` subclass for that status;
    - a body that is not a JSON object with a ``token_endpoint``:
      :class:`SerializationException`.
    """

    def __init__(self, host: str):
        """
        Validate and normalise the host. A host without a scheme gets ``https://``.

        :param host: The Zitadel instance host name or URL.
        :raises ValueError: If the host is empty, uses a scheme other than
            http or https, or is not a valid URL.
        """
        self._host_endpoint = self._normalise_host(host)
        parts = urlsplit(self._host_endpoint)
        self._well_known_url = f"{parts.scheme}://{parts.netloc}{_WELL_KNOWN_PATH}"
        self._token_endpoint: Optional[str] = None
        self._lock = threading.Lock()

    @staticmethod
    def _normalise_host(host: Optional[str]) -> str:
        trimmed = (host or "").strip()
        if not trimmed:
            raise ValueError("Host cannot be empty.")
        # noinspection HttpUrlsUsage
        if not trimmed.lower().startswith(("http://", "https://")):
            if "://" in trimmed:
                raise ValueError(f"Host must use the http or https scheme: {trimmed}")
            trimmed = "https://" + trimmed
        try:
            hostname = urlsplit(trimmed).hostname
        except ValueError as e:
            raise ValueError(f"Host is not a valid URL: {trimmed}") from e
        if not hostname:
            raise ValueError(f"Host is not a valid URL: {trimmed}")
        return trimmed

    def get_host_endpoint(self) -> str:
        """Returns the normalised host endpoint."""
        return self._host_endpoint

    def get_token_endpoint(self, api_client: ApiClient) -> str:
        """
        Returns the OAuth2 token endpoint, fetching the discovery document
        through the given API client on first access and caching the result.

        :param api_client: The shared API client used for the discovery request.
        :raises ApiException: If discovery fails at the transport or HTTP level.
        :raises SerializationException: If the discovery document is unusable.
        """
        with self._lock:
            if self._token_endpoint is None:
                self._token_endpoint = self._discover(api_client)
            return self._token_endpoint

    def _discover(self, api_client: ApiClient) -> str:
        url = self._well_known_url
        response = api_client.send_request("GET", url, {"Accept": "application/json"})
        status = response.status_code
        if status < 200 or status >= 300:
            raise self._status_exception(
                status,
                f"OpenID discovery at {url} failed with status {status}",
                response.headers,
                response.body,
            )
        try:
            document = json.loads(response.body)
        except ValueError as e:
            raise SerializationException(
                f"OpenID configuration at {url} is not a JSON object", e
            ) from e
        if not isinstance(document, dict):
            raise SerializationException(
                f"OpenID configuration at {url} is not a JSON object"
            )
        endpoint = document.get("token_endpoint")
        if not isinstance(endpoint, str) or not endpoint:
            raise SerializationException(
                f"OpenID configuration at {url} has no valid token_endpoint"
            )
        return endpoint

    @staticmethod
    def _status_exception(
        status: int, message: str, headers: Dict[str, str], body: str
    ) -> ApiException:
        exception = _STATUS_EXCEPTIONS.get(status)
        if exception is not None:
            return exception(
                message=message, response_headers=headers, response_body=body
            )
        if 400 <= status < 500:
            return ClientException(status, message, headers, body)
        if status >= 500:
            return ServerException(status, message, headers, body)
        return ApiException(status, message, headers, body)
