"""
SettingsService Integration Tests (Private Key Assertion)

This suite verifies the Zitadel SettingsService API's general settings
endpoint works when authenticating via a private key assertion:

 1. Retrieve general settings successfully with a valid private key
 2. Expect an ApiException when using an invalid private key path

Each test instantiates a new client to ensure a clean, stateless call.
"""

import os
import pathlib
from pathlib import Path

import pytest

import zitadel_client as zitadel
from zitadel_client import OpenApiError


@pytest.fixture(scope="module")
def base_url() -> str:
    """Provides the base URL for tests, skipping if unset."""
    url = os.getenv("BASE_URL")
    if not url:
        pytest.skip("Environment variable BASE_URL must be set", allow_module_level=True)
    return url


@pytest.fixture
def key_file(tmp_path: pathlib.Path) -> str:
    raw: str = os.getenv("JWT_KEY") or ""
    file_path: pathlib.Path = tmp_path / "jwt.json"
    file_path.write_text(raw)
    return str(file_path)


def test_retrieves_general_settings_with_valid_private_key(base_url: str, key_file: str) -> None:
    """Retrieves general settings successfully with a valid private key."""
    client = zitadel.Zitadel.with_private_key(
        base_url,
        key_file,
    )
    client.settings.settings_service_get_general_settings()


def test_raises_api_exception_with_invalid_private_key(key_file: str) -> None:
    """Raises ApiException when using an invalid private key path."""
    client = zitadel.Zitadel.with_private_key(
        "https://zitadel.cloud",
        key_file,
    )
    with pytest.raises(OpenApiError):
        client.settings.settings_service_get_general_settings()
