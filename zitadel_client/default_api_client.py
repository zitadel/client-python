import json
import urllib.parse
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union

import urllib3

from zitadel_client import ApiError, Configuration
from zitadel_client.i_api_client import IApiClient
from zitadel_client.object_serializer import Deserializable, ObjectSerializer

T = TypeVar("T", bound=Deserializable)


class DefaultApiClient(IApiClient):
    """
    A self-contained, urllib3-based API client implementation.

    This client supports custom PoolManager configuration via an optional callable,
    allowing proxy settings, disabling TLS verification, adding custom headers, etc.

    Example:
    ```python
    from zitadel_client.auth import PersonalAccessTokenAuthenticator
    from zitadel_client import Configuration
    from zitadel_client.default_api_client import DefaultApiClient

    config = Configuration(
        authenticator=PersonalAccessTokenAuthenticator("[https://api.example.com](https://api.example.com)", "test-token")
    )

    def client_configurator(pool_args: Dict[str, Any]) -> Dict[str, Any]:
        pool_args["cert_reqs"] = "CERT_NONE"
        pool_args["proxy_url"] = "[https://username:password@proxy.example.com:3128](https://username:password@proxy.example.com:3128)"
        pool_args["headers"] = {"X-My-Custom-Header": "custom-value"}
        return pool_args

    client = DefaultApiClient(config, client_configurator)
    ```
    """

    VALID_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}

    def __init__(
        self,
        config: Configuration,
        client_configurator: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ) -> None:
        """
        Initializes the DefaultApiClient.

        :param config: The client configuration.
        :param client_configurator: An optional callable to customize the urllib3 PoolManager.
        """
        self._config = config
        self._serde = ObjectSerializer()

        pool_args: Dict[str, Any] = {"timeout": urllib3.Timeout(connect=config.connect_timeout, total=config.timeout)}
        if client_configurator:
            pool_args = client_configurator(pool_args)
        self._pool_manager = urllib3.PoolManager(**pool_args)

    def invoke_api(  # noqa C901
        self,
        operation_id: str,
        path_template: str,
        method: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        header_params: Dict[str, Any],
        body: Optional[Any],
        success_type: Optional[Type[T]] = None,
        error_types: Optional[Dict[Union[int, str], Type[Deserializable]]] = None,
    ) -> T:
        """
        Invokes a remote API endpoint.

        :param operation_id: A unique identifier for the API operation.
        :param path_template: The URL path template (e.g., /users/{id}).
        :param method: The HTTP method (e.g., 'GET', 'POST').
        :param path_params: A dictionary of parameters to substitute into the path template.
        :param query_params: A dictionary of query parameters to append to the URL.
        :param header_params: A dictionary of custom HTTP headers.
        :param body: The request body, typically a serializable object.
        :param success_type: The expected response type for a successful (2xx) response.
        :param error_types: A map of status codes (e.g., 404, "4XX", "default") to error response types.
        :return: The deserialized response object on success, or None if the success_type is not provided.
        """
        if method.upper() not in self.VALID_METHODS:
            raise ValueError(f"Invalid HTTP method: {method}")

        final_path = self._build_path(path_template, path_params)
        url = self._config.host + final_path

        payload: Optional[bytes] = None
        default_headers: Dict[str, str] = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self._config.access_token}",
            "User-Agent": self._config.user_agent,
            "X-Operation-Id": operation_id,
        }
        headers = {**default_headers, **header_params}

        if body is not None:
            headers["Content-Type"] = "application/json"
            payload = json.dumps(self._serde.serialize(body)).encode("utf-8")

        try:
            response = self._pool_manager.request(
                method.upper(),
                url,
                body=payload,
                headers=headers,
                fields=query_params,
                preload_content=False,
            )
        except urllib3.exceptions.MaxRetryError as e:
            raise RuntimeError(f"[{operation_id}] API Request failed") from e

        response_body_bytes = response.data

        if 200 <= response.status < 300:
            if success_type and response_body_bytes:
                try:
                    decoded_body = json.loads(response_body_bytes.decode("utf-8"))
                    return self._serde.deserialize(decoded_body, success_type)
                except Exception as e:
                    raise RuntimeError(f"[{operation_id}] Failed to deserialize successful response.") from e
            return None  # type: ignore

        error_class = self._find_error_type(response.status, error_types)
        error_body: Any = None

        if response_body_bytes:
            decoded_string = response_body_bytes.decode("utf-8")
            try:
                error_body = json.loads(decoded_string)
            except json.JSONDecodeError:
                error_body = decoded_string

        if error_class and isinstance(error_body, (dict, list)):
            # noinspection PyBroadException
            try:
                error_body = self._serde.deserialize(error_body, error_class)
            except Exception:  # noqa S110
                pass

        raise ApiError(
            code=response.status,
            response_headers=dict(response.headers),
            response_body=error_body,
        )

    # noinspection PyMethodMayBeStatic
    def _find_error_type(
        self, status_code: int, error_types: Optional[Dict[Union[int, str], Type[Deserializable]]]
    ) -> Optional[Type[Deserializable]]:
        """
        Finds the appropriate error class for a given HTTP status code.

        The lookup follows a specific order of precedence:
        1. The exact status code (e.g., 404).
        2. The status code family (e.g., "4XX" for a 404 status code).
        3. A "default" key.

        :param status_code: The HTTP status code.
        :param error_types: A map of status codes to class types.
        :return: The found class type or None if no match is found.
        """
        if error_types is None:
            return None

        if status_code in error_types:
            return error_types[status_code]

        family = f"{status_code // 100}XX"
        if family in error_types:
            return error_types[family]

        if "default" in error_types:
            return error_types["default"]

        return None

    @staticmethod
    def _build_path(path_template: str, path_params: Dict[str, Any]) -> str:
        """
        Builds a URL path by substituting placeholders with encoded values.

        :param path_template: The URL path with placeholders like /users/{id}.
        :param path_params: The parameters to substitute.
        :return: The final, resolved URL path.
        """
        result = path_template
        for key, value in path_params.items():
            encoded_value = urllib.parse.quote(str(value))
            result = result.replace(f"{{{key}}}", encoded_value)
        return result
