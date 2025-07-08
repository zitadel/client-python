import uuid
from typing import Dict, Generator

import pytest
import time

import zitadel_client as zitadel
from spec.base_spec import docker_compose as docker_compose
from zitadel_client import UserServiceDeleteUserRequest
from zitadel_client.exceptions import ApiError
from zitadel_client.models import (
    UserServiceAddHumanUserRequest,
    UserServiceAddHumanUserResponse,
    UserServiceGetUserByIDResponse,
    UserServiceListUsersRequest,
    UserServiceSetHumanEmail,
    UserServiceSetHumanProfile,
    UserServiceUpdateHumanUserRequest,
   UserServiceGetUserByIDRequest,
)


@pytest.fixture(scope="module")
def client(docker_compose: Dict[str, str]) -> zitadel.Zitadel:  # noqa F811
    """Provides a Zitadel client configured with a personal access token."""
    base_url = docker_compose["base_url"]
    auth_token = docker_compose["auth_token"]
    return zitadel.Zitadel.with_access_token(base_url, auth_token)


@pytest.fixture
def user(client: zitadel.Zitadel) -> Generator[UserServiceAddHumanUserResponse, None, None]:
    """Creates a fresh human user for each test and cleans up afterward."""
    request = UserServiceAddHumanUserRequest(
        username=uuid.uuid4().hex,
        profile=UserServiceSetHumanProfile(given_name="John", family_name="Doe"),  # type: ignore[call-arg]
        email=UserServiceSetHumanEmail(email=f"johndoe{uuid.uuid4().hex}@example.com"),
    )
    response = client.users.add_human_user(request)
    print(response)
    time.sleep(4)
    yield response
    try:
        pass
    except ApiError:
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
        print(user)
        print("moo")
        print(user.user_id)
        request = UserServiceGetUserByIDRequest(
            userId=user.user_id or "",
        )
        response: UserServiceGetUserByIDResponse = client.users.get_user_by_id(request)
        print(response)
        assert response.user.user_id == user.user_id  # type: ignore[union-attr]

    def test_includes_created_user_when_listing(
        self,
        client: zitadel.Zitadel,
        user: UserServiceAddHumanUserResponse,
    ) -> None:
        """Includes the created user when listing all users."""
        request = UserServiceListUsersRequest(queries=[])
        response = client.users.list_users(request)
        ids = [u.user_id for u in response.result]  # type: ignore
        assert user.user_id in ids

    def test_updates_user_email_and_reflects_in_get(
        self,
        client: zitadel.Zitadel,
        user: UserServiceAddHumanUserResponse,
    ) -> None:
        """Updates the user's email and verifies the change."""
        request = UserServiceUpdateHumanUserRequest(
            userId=user.user_id, email=UserServiceSetHumanEmail(email=f"updated{uuid.uuid4().hex}@example.com")
        )
        client.users.update_human_user(request)
        response = client.users.get_user_by_id(UserServiceGetUserByIDRequest(
                userId=user.user_id or "",
            ))
        assert "updated" in response.user.human.email.email  # type: ignore

    def test_raises_api_exception_for_nonexistent_user(
        self,
        client: zitadel.Zitadel,
    ) -> None:
        """Raises an ApiException when retrieving a non-existent user."""
        with pytest.raises(ApiError):
            request = UserServiceGetUserByIDRequest(
                userId=str(uuid.uuid4()),
            )
            client.users.get_user_by_id(request)
