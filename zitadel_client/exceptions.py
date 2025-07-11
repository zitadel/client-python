from typing import Any, Dict, Optional, Union


class ZitadelError(Exception):
    """Base exception for all Zitadel API errors."""


class ApiError(ZitadelError):
    """
    Represents an HTTP error from the Zitadel API.

    Attributes:
      code             int HTTP status code
      response_headers Dict[str, str] HTTP response headers
      response_body Union[str, object, None] HTTP response body
    """

    def __init__(
        self,
        code: int,
        response_headers: Dict[str, str],
        response_body: Optional[Union[str, object, None]] = None,
    ) -> None:
        super().__init__(f"Error {code}")
        self.code = code
        self.response_headers = response_headers
        self.response_body = response_body
