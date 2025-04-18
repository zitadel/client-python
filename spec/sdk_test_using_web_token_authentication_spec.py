import os
import tempfile
import uuid

import pytest

import zitadel_client as zitadel
from zitadel_client.auth.web_token_authenticator import WebTokenAuthenticator


@pytest.fixture
def key_file() -> str:
    jwt_key = os.getenv("JWT_KEY")
    if jwt_key is None:
        pytest.fail("JWT_KEY is not set in the environment")
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as tf:
        tf.write(jwt_key)
        return tf.name


@pytest.fixture
def base_url() -> str | None:
    """Fixture to return the base URL."""
    return os.getenv("BASE_URL")


@pytest.fixture
def user_id(key_file: str, base_url: str) -> str | None:
    """Fixture to create a user and return their ID."""
    with zitadel.Zitadel(WebTokenAuthenticator.from_json(base_url, key_file)) as client:
        try:
            response = client.users.add_human_user(
                body=zitadel.models.V2AddHumanUserRequest(
                    username=uuid.uuid4().hex,
                    profile=zitadel.models.V2SetHumanProfile(given_name="John", family_name="Doe"),  # type: ignore[call-arg]
                    email=zitadel.models.V2SetHumanEmail(email=f"johndoe{uuid.uuid4().hex}@caos.ag"),
                )
            )
            return response.user_id
        except Exception as e:
            pytest.fail(f"Exception while creating user: {e}")


def test_should_deactivate_and_reactivate_user_with_valid_token(user_id: str, key_file: str, base_url: str) -> None:
    """Test to (de)activate the user with a valid token."""
    with zitadel.Zitadel(WebTokenAuthenticator.from_json(base_url, key_file)) as client:
        try:
            deactivate_response = client.users.deactivate_user(user_id=user_id)
            assert deactivate_response is not None, "Deactivation response is None"

            reactivate_response = client.users.reactivate_user(user_id=user_id)
            assert reactivate_response is not None, "Reactivation response is None"
        except Exception as e:
            pytest.fail(f"Exception when calling deactivate_user or reactivate_user with valid token: {e}")
