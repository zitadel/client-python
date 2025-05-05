from typing import Any, Optional

from typing_extensions import Self

import zitadel_client.rest_response


class OpenApiError(Exception):
    """The base exception class for all OpenApiErrors"""


class ApiException(OpenApiError):  # noqa N818 should be named with an Error suffix later
    def __init__(
        self,
        status: Optional[int] = None,
        reason: Optional[str] = None,
        http_resp: Optional[zitadel_client.rest_response.RESTResponse] = None,
        *,
        body: Optional[str] = None,
        data: Optional[Any] = None,
    ) -> None:
        self.status = status
        self.reason = reason
        self.body = body
        self.data = data
        self.headers = None

        if http_resp:
            if self.status is None:
                self.status = http_resp.status
            if self.reason is None:
                self.reason = http_resp.reason
            if self.body is None and http_resp.data is not None:
                # noinspection PyBroadException
                try:
                    self.body = http_resp.data.decode("utf-8")
                except Exception:  # noqa: S110
                    pass
            self.headers = http_resp.getheaders()

    @classmethod
    def from_response(
        cls,
        *,
        http_resp: zitadel_client.rest_response.RESTResponse,
        body: Optional[str],
        data: Optional[Any],
    ) -> Self:
        if http_resp.status == 400:
            raise ApiException(http_resp=http_resp, body=body, data=data)

        if http_resp.status == 401:
            raise ApiException(http_resp=http_resp, body=body, data=data)

        if http_resp.status == 403:
            raise ApiException(http_resp=http_resp, body=body, data=data)

        if http_resp.status == 404:
            raise ApiException(http_resp=http_resp, body=body, data=data)

        # Added new conditions for 409 and 422
        if http_resp.status == 409:
            raise ApiException(http_resp=http_resp, body=body, data=data)

        if http_resp.status == 422:
            raise ApiException(http_resp=http_resp, body=body, data=data)

        if 500 <= http_resp.status <= 599:
            raise ApiException(http_resp=http_resp, body=body, data=data)
        raise ApiException(http_resp=http_resp, body=body, data=data)

    def __str__(self) -> str:
        """Custom error messages for exception"""
        error_message = "({0})\nReason: {1}\n".format(self.status, self.reason)
        if self.headers:
            error_message += "HTTP response headers: {0}\n".format(self.headers)

        if self.data or self.body:
            error_message += "HTTP response body: {0}\n".format(self.data or self.body)

        return error_message
