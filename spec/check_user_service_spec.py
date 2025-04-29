import os
import pprint
import uuid
from typing import Generator

import pytest

import zitadel_client as zitadel
from zitadel_client.exceptions import ApiException
from zitadel_client.models import (
    UserServiceAddHumanUserRequest,
    UserServiceAddHumanUserResponse,
    UserServiceGetUserByIDResponse,
    UserServiceListUsersRequest,
    UserServiceSetHumanEmail,
    UserServiceSetHumanProfile,
    UserServiceUpdateHumanUserRequest,
)


# noinspection DuplicatedCode
@pytest.fixture(scope="module")
def base_url() -> str:
    """Provides the base URL for tests, skipping if unset."""
    url = os.getenv("BASE_URL")
    if not url:
        pytest.skip("Environment variable BASE_URL must be set", allow_module_level=True)
    return url


@pytest.fixture(scope="module")
def auth_token() -> str:
    """Provides a valid personal access token, skipping if unset."""
    token = os.getenv("AUTH_TOKEN")
    if not token:
        pytest.skip("Environment variable AUTH_TOKEN must be set", allow_module_level=True)
    return token


@pytest.fixture(scope="module")
def client(base_url: str, auth_token: str) -> zitadel.Zitadel:
    """Provides a Zitadel client configured with a personal access token."""
    return zitadel.Zitadel.with_access_token(base_url, auth_token)


@pytest.fixture
def user(client: zitadel.Zitadel) -> Generator[UserServiceAddHumanUserResponse, None, None]:
    """Creates a fresh human user for each test and cleans up afterward."""
    request = UserServiceAddHumanUserRequest(
        username=uuid.uuid4().hex,
        profile=UserServiceSetHumanProfile(given_name="John", family_name="Doe"),  # type: ignore[call-arg]
        email=UserServiceSetHumanEmail(email=f"johndoe{uuid.uuid4().hex}@example.com"),
    )
    response = client.users.user_service_add_human_user(request)
    yield response
    try:
        client.users.user_service_delete_user(response.user_id)  # type: ignore[arg-type]
    except ApiException:
        pass


class TestUserServiceSanityCheckSpec:
    """
    UserService Integration Tests

    This suite verifies the Zitadel UserService API's basic operations using a
    personal access token:

     1. Create a human user
     2. Retrieve the user by ID
     3. List users and ensure the created user appears
     4. Update the user's email and confirm the change
     5. Error when retrieving a non-existent user

    Each test runs in isolation: a new user is created in the `user` fixture and
    removed after the test to ensure a clean state.
    """

    def test_retrieves_user_details_by_id(
        self,
        client: zitadel.Zitadel,
        user: UserServiceAddHumanUserResponse,
    ) -> None:
        """Retrieves the user details by ID."""
        response: UserServiceGetUserByIDResponse = client.users.user_service_get_user_by_id(user.user_id)  # type: ignore[arg-type]
        assert response.user.user_id == user.user_id  # type: ignore[union-attr]

    def test_includes_created_user_when_listing(
        self,
        client: zitadel.Zitadel,
        user: UserServiceAddHumanUserResponse,
    ) -> None:
        """Includes the created user when listing all users."""
        request = UserServiceListUsersRequest(queries=[])
        response = client.users.user_service_list_users(request)
        ids = [u.user_id for u in response.result]  # type: ignore
        assert user.user_id in ids

    def test_updates_user_email_and_reflects_in_get(
        self,
        client: zitadel.Zitadel,
        user: UserServiceAddHumanUserResponse,
    ) -> None:
        """Updates the user's email and verifies the change."""
        client.users.user_service_update_human_user(
            user.user_id,  # type: ignore[arg-type]
            UserServiceUpdateHumanUserRequest(email=UserServiceSetHumanEmail(email=f"updated{uuid.uuid4().hex}@example.com")),
        )
        response = client.users.user_service_get_user_by_id(user.user_id)  # type: ignore[arg-type]
        assert "updated" in response.user.human.email.email  # type: ignore

    def test_raises_api_exception_for_nonexistent_user(
        self,
        client: zitadel.Zitadel,
    ) -> None:
        """Raises an ApiException when retrieving a non-existent user."""
        with pytest.raises(ApiException):
            client.users.user_service_get_user_by_id(str(uuid.uuid4()))
