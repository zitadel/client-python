from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar

from zitadel_client.object_serializer import Deserializable

T = TypeVar("T")


class IApiClient(ABC):
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
        response_types: Dict[int, Type[Deserializable]],
    ) -> Optional[Deserializable]:
        raise NotImplementedError
