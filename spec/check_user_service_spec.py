import uuid
from typing import AsyncGenerator, Dict

import pytest

from spec.base_spec import docker_compose as docker_compose
from zitadel_client import UserServiceDeleteUserRequest
from zitadel_client.auth.personal_access_token_authenticator import (
    PersonalAccessTokenAuthenticator,
)
from zitadel_client.errors import ApiException
from zitadel_client.models import (
    UserServiceAddHumanUserRequest,
    UserServiceAddHumanUserResponse,
    UserServiceGetUserByIDRequest,
    UserServiceGetUserByIDResponse,
    UserServiceListUsersRequest,
    UserServiceSetHumanEmail,
    UserServiceSetHumanProfile,
    UserServiceUpdateHumanUserRequest,
)
from zitadel_client.zitadel import Zitadel


@pytest.fixture(scope="module")
def client(docker_compose: Dict[str, str]) -> Zitadel:  # noqa F811
    """Provides a Zitadel client configured with a personal access token."""
    base_url = docker_compose["base_url"]
    auth_token = docker_compose["auth_token"]
    return Zitadel.with_authenticator(
        PersonalAccessTokenAuthenticator(base_url, auth_token)
    )


@pytest.fixture
async def user(
    client: Zitadel,
) -> AsyncGenerator[UserServiceAddHumanUserResponse, None]:
    """Creates a fresh human user for each test and cleans up afterward."""
    request = UserServiceAddHumanUserRequest(
        username=uuid.uuid4().hex,
        profile=UserServiceSetHumanProfile(given_name="John", family_name="Doe"),  # type: ignore[call-arg]
        email=UserServiceSetHumanEmail(email=f"johndoe{uuid.uuid4().hex}@example.com"),
    )
    response = await client.user_service.add_human_user(request)
    yield response
    try:
        await client.user_service.delete_user(
            UserServiceDeleteUserRequest(userId=response.user_id or "")
        )
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

    async def test_retrieves_user_details_by_id(
        self,
        client: Zitadel,
        user: UserServiceAddHumanUserResponse,
    ) -> None:
        """Retrieves the user details by ID."""
        request = UserServiceGetUserByIDRequest(
            userId=user.user_id or "",
        )
        response: UserServiceGetUserByIDResponse = (
            await client.user_service.get_user_by_id(request)
        )
        assert response.user.user_id == user.user_id  # type: ignore[union-attr]

    async def test_includes_created_user_when_listing(
        self,
        client: Zitadel,
        user: UserServiceAddHumanUserResponse,
    ) -> None:
        """Includes the created user when listing all users."""
        request = UserServiceListUsersRequest(queries=[])
        response = await client.user_service.list_users(request)
        ids = [u.user_id for u in response.result]  # type: ignore
        assert user.user_id in ids

    async def test_updates_user_email_and_reflects_in_get(
        self,
        client: Zitadel,
        user: UserServiceAddHumanUserResponse,
    ) -> None:
        """Updates the user's email and verifies the change."""
        request = UserServiceUpdateHumanUserRequest(
            userId=user.user_id,
            email=UserServiceSetHumanEmail(
                email=f"updated{uuid.uuid4().hex}@example.com"
            ),
        )
        await client.user_service.update_human_user(request)
        response = await client.user_service.get_user_by_id(
            UserServiceGetUserByIDRequest(
                userId=user.user_id or "",
            )
        )
        assert "updated" in response.user.human.email.email  # type: ignore

    async def test_raises_api_exception_for_nonexistent_user(
        self,
        client: Zitadel,
    ) -> None:
        """Raises an ApiException when retrieving a non-existent user."""
        with pytest.raises(ApiException):
            request = UserServiceGetUserByIDRequest(
                userId=str(uuid.uuid4()),
            )
            await client.user_service.get_user_by_id(request)
