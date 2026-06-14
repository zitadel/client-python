import uuid
from datetime import timedelta
from typing import AsyncGenerator, Dict

import pytest

from spec.base_spec import docker_compose as docker_compose
from zitadel_client.errors import ApiException
from zitadel_client.models import (
    SessionServiceChecks,
    SessionServiceCheckUser,
    SessionServiceCreateSessionRequest,
    SessionServiceCreateSessionResponse,
    SessionServiceDeleteSessionRequest,
    SessionServiceGetSessionRequest,
    SessionServiceGetSessionResponse,
    SessionServiceListSessionsRequest,
    SessionServiceSetSessionRequest,
    UserServiceAddHumanUserRequest,
    UserServiceSetHumanEmail,
    UserServiceSetHumanProfile,
)
from zitadel_client.zitadel import Zitadel


@pytest.fixture(scope="module")
def client(docker_compose: Dict[str, str]) -> Zitadel:  # noqa F811
    """Provides a Zitadel client configured with a personal access token."""
    base_url = docker_compose["base_url"]
    auth_token = docker_compose["auth_token"]
    return Zitadel.with_access_token(base_url, auth_token)


@pytest.fixture
async def session(
    client: Zitadel,
) -> AsyncGenerator[SessionServiceCreateSessionResponse, None]:
    """Creates a fresh session for each test and cleans up afterward."""
    username = uuid.uuid4().hex
    request1 = UserServiceAddHumanUserRequest(
        username=username,
        profile=UserServiceSetHumanProfile(given_name="John", family_name="Doe"),  # type: ignore[call-arg]
        email=UserServiceSetHumanEmail(email=f"johndoe{uuid.uuid4().hex}@example.com"),
    )
    await client.users.add_human_user(request1)

    request = SessionServiceCreateSessionRequest(
        checks=SessionServiceChecks(user=SessionServiceCheckUser(loginName=username)),
        lifetime=timedelta(seconds=18000),
    )
    response = await client.sessions.create_session(request)
    yield response
    # Teardown
    delete_body = SessionServiceDeleteSessionRequest(
        sessionId=response.session_id if response.session_id is not None else "",
    )
    try:
        await client.sessions.delete_session(
            delete_body,
        )
    except ApiException:
        pass


class TestSessionServiceSanityCheckSpec:
    """
    SessionService Integration Tests

    This suite verifies the Zitadel SessionService API's basic operations using a
    personal access token:

     1. Create a session with specified checks and lifetime
     2. Retrieve the session by ID
     3. List sessions and ensure the created session appears
     4. Update the session's lifetime and confirm a new token is returned
     5. Error when retrieving a non-existent session

    Each test runs in isolation: a new session is created in the `session` fixture and
    deleted after the test to ensure a clean state.
    """

    async def test_retrieves_session_details_by_id(
        self,
        client: Zitadel,
        session: SessionServiceCreateSessionResponse,
    ) -> None:
        """Retrieves the session details by ID."""
        request = SessionServiceGetSessionRequest(
            sessionId=session.session_id if session.session_id is not None else ""
        )
        response: SessionServiceGetSessionResponse = await client.sessions.get_session(
            request
        )
        assert response.session is not None
        assert response.session.id == session.session_id

    async def test_includes_created_session_when_listing(
        self,
        client: Zitadel,
        session: SessionServiceCreateSessionResponse,
    ) -> None:
        """Includes the created session when listing all sessions."""
        request = SessionServiceListSessionsRequest(queries=[])
        response = await client.sessions.list_sessions(request)
        assert response.sessions is not None
        assert session.session_id in [session.id for session in response.sessions]

    async def test_updates_session_lifetime_and_returns_new_token(
        self,
        client: Zitadel,
        session: SessionServiceCreateSessionResponse,
    ) -> None:
        """Updates the session lifetime and returns a new token."""
        request = SessionServiceSetSessionRequest(
            sessionId=session.session_id if session.session_id is not None else "",
            lifetime=timedelta(seconds=36000),
        )
        response = await client.sessions.set_session(request)
        assert isinstance(response.session_token, str)

    async def test_raises_api_exception_for_nonexistent_session(
        self,
        client: Zitadel,
        session: SessionServiceCreateSessionResponse,
    ) -> None:
        """Raises an ApiException when retrieving a non-existent session."""
        with pytest.raises(ApiException):
            request = SessionServiceGetSessionRequest(
                sessionId=str(uuid.uuid4()),
                sessionToken=session.session_token,
            )
            await client.sessions.get_session(request)
