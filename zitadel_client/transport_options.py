from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass(frozen=True)
class TransportOptions:
    """Immutable transport options for configuring HTTP connections."""

    default_headers: Dict[str, str] = field(default_factory=dict)
    ca_cert_path: Optional[str] = None
    insecure: bool = False
    proxy_url: Optional[str] = None

    @staticmethod
    def defaults() -> "TransportOptions":
        return TransportOptions()
