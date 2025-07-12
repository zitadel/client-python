import io
from typing import Dict, Optional

from urllib3 import BaseHTTPResponse


class RESTResponse(io.IOBase):
    data: Optional[bytes] = None

    def __init__(self, resp: BaseHTTPResponse, *args, **kwargs) -> None:  # type: ignore
        # noinspection PyArgumentList
        super().__init__(*args, **kwargs)
        self.response = resp
        self.status = resp.status
        self.reason = resp.reason
        self.data = None

    def read(self) -> Optional[bytes]:
        if self.data is None:
            self.data = self.response.data
        return self.data

    def getheaders(self) -> Dict[str, str]:
        """Returns a dictionary of the response headers."""
        return dict(self.response.headers)

    def getheader(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Returns a given response header."""
        return self.response.headers.get(name, default)
