from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar, Union

from zitadel_client.object_serializer import Deserializable

T = TypeVar("T", bound=Deserializable)


class IApiClient(ABC):
    """
    Defines the contract for an API client that can invoke API operations.
    """

    @abstractmethod
    def invoke_api(
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
        raise NotImplementedError
