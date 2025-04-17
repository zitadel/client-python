import os
import uuid

import pytest

import zitadel_client as zitadel
from zitadel_client.auth.client_credentials_authenticator import ClientCredentialsAuthenticator


@pytest.fixture
def client_id() -> str | None:
    """Fixture to return a valid personal access token."""
    return os.getenv("CLIENT_ID")


@pytest.fixture
def client_secret() -> str | None:
    """Fixture to return a valid personal access token."""
    return os.getenv("CLIENT_SECRET")


@pytest.fixture
def base_url() -> str | None:
    """Fixture to return the base URL."""
    return os.getenv("BASE_URL")


@pytest.fixture
def user_id(client_id: str, client_secret: str, base_url: str) -> str | None:
    """Fixture to create a user and return their ID."""
    with zitadel.Zitadel(ClientCredentialsAuthenticator.builder(base_url, client_id, client_secret).build()) as client:
        try:
            response = client.users.add_human_user(
                body=zitadel.models.V2AddHumanUserRequest(
                    username=uuid.uuid4().hex,
                    profile=zitadel.models.V2SetHumanProfile(given_name="John", family_name="Doe"), # type: ignore[call-arg]
                    email=zitadel.models.V2SetHumanEmail(email=f"johndoe{uuid.uuid4().hex}@caos.ag")
                )
            )
            print("User created:", response)
            return response.user_id
        except Exception as e:
            pytest.fail(f"Exception while creating user: {e}")


def test_should_deactivate_and_reactivate_user_with_valid_token(user_id: str, client_id: str, client_secret: str, base_url: str) -> None:
    """Test to (de)activate the user with a valid token."""
    with zitadel.Zitadel(ClientCredentialsAuthenticator.builder(base_url, client_id, client_secret).build()) as client:
        try:
            deactivate_response = client.users.deactivate_user(user_id=user_id)
            print("User deactivated:", deactivate_response)

            reactivate_response = client.users.reactivate_user(user_id=user_id)
            print("User reactivated:", reactivate_response)
            # Adjust based on actual response format
            # assert reactivate_response["status"] == "success"
        except Exception as e:
            pytest.fail(f"Exception when calling deactivate_user or reactivate_user with valid token: {e}")


def test_should_not_deactivate_or_reactivate_user_with_invalid_token(user_id: str, base_url: str) -> None:
    """Test to attempt (de)activating the user with an invalid token."""
    with zitadel.Zitadel(ClientCredentialsAuthenticator.builder(base_url, "id", "secret").build()) as client:
        try:
            client.users.deactivate_user(user_id=user_id)
            pytest.fail("Expected exception when deactivating user with invalid token, but got response.")
        except Exception as e:
            print("Caught expected UnauthorizedException:", e)

        try:
            client.users.reactivate_user(user_id=user_id)
            pytest.fail("Expected exception when reactivating user with invalid token, but got response.")
        except Exception as e:
            print("Caught expected UnauthorizedException:", e)
