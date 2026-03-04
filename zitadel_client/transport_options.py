from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Optional


@dataclass(frozen=True)
class TransportOptions:
    """Immutable transport options for configuring HTTP connections."""

    default_headers: Mapping[str, str] = field(default_factory=dict)
    ca_cert_path: Optional[str] = None
    insecure: bool = False
    proxy_url: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "default_headers", MappingProxyType(dict(self.default_headers)))

    @staticmethod
    def defaults() -> "TransportOptions":
        return TransportOptions()
