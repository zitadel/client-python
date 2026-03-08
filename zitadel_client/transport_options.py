from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Optional


@dataclass(frozen=True)
class TransportOptions:
    """Immutable transport options for configuring HTTP connections.

    :param default_headers: Additional HTTP headers to include in every request.
    :param ca_cert_path: Path to a custom CA certificate file for TLS verification.
    :param insecure: If True, disables TLS certificate verification.
    :param proxy_url: HTTP/HTTPS proxy URL to route requests through.
    """

    default_headers: Mapping[str, str] = field(default_factory=dict)
    ca_cert_path: Optional[str] = None
    insecure: bool = False
    proxy_url: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "default_headers", MappingProxyType(dict(self.default_headers)))

    @staticmethod
    def defaults() -> "TransportOptions":
        """Returns a TransportOptions instance with all default values."""
        return TransportOptions()

    def to_session_kwargs(self) -> dict:
        """Builds keyword arguments for an authlib OAuth2Session."""
        kwargs: dict = {}
        if self.insecure:
            kwargs["verify"] = False
        elif self.ca_cert_path:
            kwargs["verify"] = self.ca_cert_path
        if self.proxy_url:
            kwargs["proxies"] = {"http": self.proxy_url, "https": self.proxy_url}
        return kwargs
