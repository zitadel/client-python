import uuid
from typing import Dict, Generator

import pytest

import zitadel_client as zitadel
from spec.base_spec import docker_compose as docker_compose
from zitadel_client.exceptions import ApiError
from zitadel_client.models import (
    SessionServiceChecks,
    SessionServiceCheckUser,
    SessionServiceCreateSessionRequest,
    SessionServiceCreateSessionResponse,
    SessionServiceDeleteSessionRequest,
    SessionServiceGetSessionResponse,
    SessionServiceListSessionsRequest,
    SessionServiceSetSessionRequest,
    UserServiceAddHumanUserRequest,
    UserServiceSetHumanEmail,
    UserServiceSetHumanProfile,
    SessionServiceGetSessionRequest
)


@pytest.fixture(scope="module")
def client(docker_compose: Dict[str, str]) -> zitadel.Zitadel:  # noqa F811
    """Provides a Zitadel client configured with a personal access token."""
    base_url = docker_compose["base_url"]
    auth_token = docker_compose["auth_token"]
    return zitadel.Zitadel.with_access_token(base_url, auth_token)


@pytest.fixture
def session(client: zitadel.Zitadel) -> Generator[SessionServiceCreateSessionResponse, None, None]:
    """Creates a fresh session for each test and cleans up afterward."""
    username = uuid.uuid4().hex
    request1 = UserServiceAddHumanUserRequest(
        username=username,
        profile=UserServiceSetHumanProfile(given_name="John", family_name="Doe"),  # type: ignore[call-arg]
        email=UserServiceSetHumanEmail(email=f"johndoe{uuid.uuid4().hex}@example.com"),
    )
    client.users.add_human_user(request1)

    request = SessionServiceCreateSessionRequest(
        checks=SessionServiceChecks(user=SessionServiceCheckUser(loginName=username)),
        lifetime="18000s",
    )
    response = client.sessions.create_session(request)
    yield response
    # Teardown
    delete_body = SessionServiceDeleteSessionRequest(
        sessionId=response.session_id if response.session_id is not None else "",
    )
    try:
        client.sessions.delete_session(
            delete_body,
        )
    except ApiError:
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

    def test_retrieves_session_details_by_id(
        self,
        client: zitadel.Zitadel,
        session: SessionServiceCreateSessionResponse,
    ) -> None:
        """Retrieves the session details by ID."""
        request = SessionServiceGetSessionRequest(sessionId=session.session_id if session.session_id is not None else "")
        response: SessionServiceGetSessionResponse = client.sessions.get_session(request)
        assert response.session is not None
        assert response.session.id == session.session_id

    def test_includes_created_session_when_listing(
        self,
        client: zitadel.Zitadel,
        session: SessionServiceCreateSessionResponse,
    ) -> None:
        """Includes the created session when listing all sessions."""
        request = SessionServiceListSessionsRequest(queries=[])
        response = client.sessions.list_sessions(request)
        assert response.sessions is not None
        assert session.session_id in [session.id for session in response.sessions]

    def test_updates_session_lifetime_and_returns_new_token(
        self,
        client: zitadel.Zitadel,
        session: SessionServiceCreateSessionResponse,
    ) -> None:
        """Updates the session lifetime and returns a new token."""
        request = SessionServiceSetSessionRequest(
            sessionId=session.session_id if session.session_id is not None else "", lifetime="36000s"
        )
        response = client.sessions.set_session(request)
        assert isinstance(response.session_token, str)

    def test_raises_api_exception_for_nonexistent_session(
        self,
        client: zitadel.Zitadel,
        session: SessionServiceCreateSessionResponse,
    ) -> None:
        """Raises an ApiException when retrieving a non-existent session."""
        with pytest.raises(ApiError):
            request = SessionServiceGetSessionRequest(
                sessionId=str(uuid.uuid4()),
                sessionToken=session.session_token,
            )
            client.sessions.get_session(request)
