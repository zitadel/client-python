from __future__ import annotations

from typing import Generic, Mapping, Optional, TypeVar

from pydantic import BaseModel, Field, StrictBytes, StrictInt

T = TypeVar("T")


# noinspection PyTypeHints
class ApiResponse(BaseModel, Generic[T]):
    """
    API response object
    """

    status_code: StrictInt = Field(description="HTTP status code")
    headers: Optional[Mapping[str, str]] = Field(None, description="HTTP headers")
    data: T = Field(description="Deserialized data given the data type")
    raw_data: StrictBytes = Field(description="Raw data (HTTP response body)")

    model_config = {"arbitrary_types_allowed": True}
