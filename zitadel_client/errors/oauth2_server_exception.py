from typing import Optional

from zitadel_client.errors import ZitadelException


class OAuth2ServerException(ZitadelException):
    """Exception for an OAuth2 token endpoint that answered with a non-2xx status.

    Carries the RFC 6749 section 5.2 error fields when the response body holds
    a well-formed OAuth2 error object, and the raw body in every case.
    """

    def __init__(
        self,
        status_code: int,
        code: Optional[str],
        description: Optional[str],
        uri: Optional[str],
        raw_body: str,
    ) -> None:
        if code is None:
            message = f"Token request failed with status {status_code}: {raw_body}"
        elif description is not None:
            message = f"Token request failed with status {status_code}: {code} -- {description}"
        else:
            message = f"Token request failed with status {status_code}: {code}"
        super().__init__(message)
        self._status_code = status_code
        self._code = code
        self._description = description
        self._uri = uri
        self._raw_body = raw_body

    @property
    def status_code(self) -> int:
        """The HTTP status code of the token response."""
        return self._status_code

    @property
    def code(self) -> Optional[str]:
        """The RFC 6749 error code, or ``None`` when the body held no OAuth2 error object."""
        return self._code

    @property
    def description(self) -> Optional[str]:
        """The human-readable error description, if present."""
        return self._description

    @property
    def uri(self) -> Optional[str]:
        """A URI describing the error, if present."""
        return self._uri

    @property
    def raw_body(self) -> str:
        """The raw token response body."""
        return self._raw_body
