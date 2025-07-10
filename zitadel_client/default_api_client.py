import json
import urllib.parse
from typing import Any, Callable, Dict, Optional, Type, TypeVar

from zitadel_client import ApiError, Configuration
from zitadel_client.i_api_client import IApiClient
from zitadel_client.object_serializer import ObjectSerializer

T = TypeVar("T")


class DefaultApiClient(IApiClient):
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
        response_types: Dict[int, Type[T]],
    ) -> Optional[T]:
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
                return ObjectSerializer.deserialize(response_body, response_cls)
            else:
                return None
        elif response_cls:
            try:
                error_body = ObjectSerializer.deserialize(response_body, response_cls)
            except Exception:
                error_body = response_body
            raise ApiError(
                status=response.status,
                headers=response.headers,
                body=error_body,
            )
        else:
            raise ApiError(
                status=response.status,
                headers=response.headers,
                body=response_body,
            )

    @staticmethod
    def _build_path(path_template: str, path_params: Dict[str, Any]) -> str:
        result = path_template
        for key, value in path_params.items():
            encoded_value = urllib.parse.quote(str(value))
            result = result.replace(f"{{{key}}}", encoded_value)
        return result
