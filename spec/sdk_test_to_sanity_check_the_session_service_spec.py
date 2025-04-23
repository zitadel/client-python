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

import os
import uuid
from typing import Generator

import pytest

import zitadel_client as zitadel
from zitadel_client.exceptions import ApiException
from zitadel_client.models import (
    SessionServiceChecks,
    SessionServiceCheckUser,
    SessionServiceCreateSessionRequest,
    SessionServiceCreateSessionResponse,
    SessionServiceDeleteSessionBody,
    SessionServiceGetSessionResponse,
    SessionServiceListSessionsRequest,
    SessionServiceListSessionsResponse,
    SessionServiceSetSessionRequest,
    SessionServiceSetSessionResponse,
)


def pytest_configure() -> None:
    """Skip tests if required environment variables are missing."""
    if not os.getenv("AUTH_TOKEN") or not os.getenv("BASE_URL"):
        pytest.skip(
            "Environment variables AUTH_TOKEN and BASE_URL must be set",
            allow_module_level=True,
        )


@pytest.fixture(scope="module")
def client() -> zitadel.Zitadel:
    """Provides a Zitadel client configured with a personal access token."""
    token: str = os.getenv("AUTH_TOKEN")  # type: ignore
    base_url: str = os.getenv("BASE_URL")  # type: ignore
    return zitadel.Zitadel.with_access_token(base_url, token)


@pytest.fixture
def session(client: zitadel.Zitadel) -> Generator[SessionServiceCreateSessionResponse, None, None]:
    """Creates a fresh session for each test and cleans up afterward."""
    request = SessionServiceCreateSessionRequest(
        checks=SessionServiceChecks(
            user=SessionServiceCheckUser(loginName="johndoe")
        ),
        lifetime="18000s",
    )
    response = client.sessions.session_service_create_session(request)
    yield response
    # Teardown
    delete_body = SessionServiceDeleteSessionBody()
    try:
        client.sessions.session_service_delete_session(
            response.session_id if response.session_id is not None else "",
            delete_body,
        )
    except ApiException:
        pass


class TestSessionServiceSanityCheckSpec:
    """
    Integration tests for the SessionService endpoints.

    Verifies create, get, list, set, and error behaviors for sessions.
    """

    def test_retrieves_session_details_by_id(
        self,
        client: zitadel.Zitadel,
        session: SessionServiceCreateSessionResponse,
    ) -> None:
        """Retrieves the session details by ID."""
        response: SessionServiceGetSessionResponse = (
            client.sessions.session_service_get_session(
                session.session_id if session.session_id is not None else ""
            )
        )
        assert response.session is not None
        assert response.session.id == session.session_id

    def test_includes_created_session_when_listing(
        self,
        client: zitadel.Zitadel,
        session: SessionServiceCreateSessionResponse,
    ) -> None:
        """Includes the created session when listing all sessions."""
        request = SessionServiceListSessionsRequest(queries=[])
        response: SessionServiceListSessionsResponse = (
            client.sessions.session_service_list_sessions(request)
        )
        assert response.sessions is not None
        assert session.session_id in [session.id for session in response.sessions]

    def test_updates_session_lifetime_and_returns_new_token(
        self,
        client: zitadel.Zitadel,
        session: SessionServiceCreateSessionResponse,
    ) -> None:
        """Updates the session lifetime and returns a new token."""
        request = SessionServiceSetSessionRequest(lifetime="36000s")
        response: SessionServiceSetSessionResponse = (
            client.sessions.session_service_set_session(
                session.session_id if session.session_id is not None else "",
                request,
            )
        )
        assert isinstance(response.session_token, str)

    def test_raises_api_exception_for_nonexistent_session(
        self,
        client: zitadel.Zitadel,
        session: SessionServiceCreateSessionResponse,
    ) -> None:
        """Raises an ApiException when retrieving a non-existent session."""
        with pytest.raises(ApiException):
            client.sessions.session_service_get_session(
                str(uuid.uuid4()),
                session_token=session.session_token,
            )
