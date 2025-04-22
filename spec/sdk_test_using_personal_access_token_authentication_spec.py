import os
import uuid

import pytest

import zitadel_client as zitadel
from zitadel_client.exceptions import UnauthorizedException


@pytest.fixture
def valid_token() -> str | None:
    """Fixture to return a valid personal access token."""
    return os.getenv("AUTH_TOKEN")


@pytest.fixture
def invalid_token() -> str | None:
    """Fixture to return an invalid token."""
    return "whoops"


@pytest.fixture
def base_url() -> str | None:
    """Fixture to return the base URL."""
    return os.getenv("BASE_URL")


@pytest.fixture
def user_id(valid_token: str, base_url: str) -> str | None:
    """Fixture to create a user and return their ID."""
    with zitadel.Zitadel.with_access_token(base_url, valid_token) as client:
        try:
            response = client.users.user_service_add_human_user(
                zitadel.models.UserServiceAddHumanUserRequest(
                    username=uuid.uuid4().hex,
                    profile=zitadel.models.UserServiceSetHumanProfile(given_name="John", family_name="Doe"),  # type: ignore[call-arg]
                    email=zitadel.models.UserServiceSetHumanEmail(email=f"johndoe{uuid.uuid4().hex}@caos.ag"),
                )
            )
            return response.user_id
        except Exception as e:
            pytest.fail(f"Exception while creating user: {e}")


def test_should_deactivate_and_reactivate_user_with_valid_token(user_id: str, valid_token: str, base_url: str) -> None:
    """Test to (de)activate the user with a valid token."""
    with zitadel.Zitadel.with_access_token(base_url, valid_token) as client:
        try:
            deactivate_response = client.users.user_service_deactivate_user(user_id=user_id)
            assert deactivate_response is not None, "Deactivation response is None"

            reactivate_response = client.users.user_service_reactivate_user(user_id=user_id)
            assert reactivate_response is not None, "Reactivation response is None"
        except Exception as e:
            pytest.fail(f"Exception when calling deactivate_user or reactivate_user with valid token: {e}")


def test_should_not_deactivate_or_reactivate_user_with_invalid_token(user_id: str, invalid_token: str, base_url: str) -> None:
    """Test to attempt (de)activating the user with an invalid token."""
    with zitadel.Zitadel.with_access_token(base_url, invalid_token) as client:
        with pytest.raises(UnauthorizedException):
            client.users.user_service_deactivate_user(user_id=user_id)

        with pytest.raises(UnauthorizedException):
            client.users.user_service_reactivate_user(user_id=user_id)
