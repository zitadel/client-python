import json
import urllib.parse
from typing import Any, Callable, Dict, Optional, Type, TypeVar

import urllib3

from zitadel_client import ApiError, Configuration
from zitadel_client.i_api_client import IApiClient
from zitadel_client.object_serializer import Deserializable, ObjectSerializer

T = TypeVar("T")


class DefaultApiClient(IApiClient):
    """
    A self-contained, urllib3-based API client.

    This client supports custom PoolManager configuration via an optional callable,
    allowing proxy settings, disabling TLS verification, adding custom headers, etc.

    Example:
    ```python
    from zitadel_client.auth import PersonalAccessTokenAuthenticator
    from zitadel_client import Configuration
    from zitadel_client.default_api_client import DefaultApiClient

    # 1) Create Configuration with NoAuthAuthenticator
    config = Configuration(
        authenticator=PersonalAccessTokenAuthenticator("https://api.example.com", "test-token")
    )

    # 2) Define a configurator for proxy, headers, and disable TLS
    def client_configurator(pool_args: Dict[str, Any]) -> Dict[str, Any]:
        # Disable TLS certificate verification
        pool_args["cert_reqs"] = "CERT_NONE"
        # Set HTTP/S proxy
        pool_args["proxy_url"] = "https://username:password@proxy.example.com:3128"
        # Add a custom header to every request
        pool_args["headers"] = {"X-My-Custom-Header": "custom-value"}
        return pool_args

    # 3) Instantiate DefaultApiClient with configurator
    client = DefaultApiClient(config, client_configurator)
    ```
    """

    VALID_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}

    def __init__(
        self, config: Configuration, client_configurator: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
    ) -> None:
        import urllib3

        self._config = config

        pool_args: Dict[str, Any] = {"timeout": urllib3.Timeout(connect=config.connect_timeout, total=config.timeout)}

        if client_configurator:
            pool_args = client_configurator(pool_args)

        self._pool_manager = urllib3.PoolManager(**pool_args)

    def invoke_api(
        self,
        operation_id: str,
        path_template: str,
        method: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        header_params: Dict[str, Any],
        body: Optional[Any],
        response_types: Dict[int, Type[Deserializable]],
    ) -> Optional[Deserializable]:
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
            payload = json.dumps(ObjectSerializer.sanitize_for_serialization(body)).encode("utf-8")

        try:
            response = self._pool_manager.request(
                method.upper(),
                url,
                body=payload,
                headers=headers,
                fields=query_params,
            )
        except urllib3.exceptions.MaxRetryError as e:
            raise RuntimeError(f"[{operation_id}] API Request failed") from e

        response_cls = response_types.get(response.status)

        try:
            response_body: Any = json.loads(response.data.decode("utf-8"))
        except json.JSONDecodeError:
            response_body = response.data.decode("utf-8")

        if 200 <= response.status < 300:
            if response_cls:
                ff = response_cls
                return ObjectSerializer.deserialize(response_body, ff)
            else:
                return None
        elif response_cls:
            try:
                error_body = ObjectSerializer.deserialize(response_body, response_cls)
            except Exception:
                error_body = response_body
            raise ApiError(
                code=response.status,
                response_headers=dict(response.headers),
                response_body=error_body,
            )
        else:
            raise ApiError(
                code=response.status,
                response_headers=dict(response.headers),
                response_body=response_body,
            )

    @staticmethod
    def _build_path(path_template: str, path_params: Dict[str, Any]) -> str:
        result = path_template
        for key, value in path_params.items():
            encoded_value = urllib.parse.quote(str(value))
            result = result.replace(f"{{{key}}}", encoded_value)
        return result
