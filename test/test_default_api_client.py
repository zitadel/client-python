import json
import time
from typing import Any, Dict, Iterator

import pytest
import urllib3
from testcontainers.core.container import DockerContainer
from typing_extensions import Self

from zitadel_client import ApiError, Configuration
from zitadel_client.auth.no_auth_authenticator import NoAuthAuthenticator
from zitadel_client.default_api_client import DefaultApiClient


class SuccessModel:
    """
    Success model to map the successful API response.
    """

    def __init__(self, status: str) -> None:
        self.status = status

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Self:
        return cls(status=data["status"])


class ErrorModel:
    """
    Error model to map the error API response.
    """

    def __init__(self, error_code: str, error_message: str) -> None:
        self.error_code = error_code
        self.error_message = error_message

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Self:
        code = data.get("errorCode") or data.get("error_code") or ""
        msg = data.get("error_message") or data.get("errorMessage") or ""
        return cls(error_code=code, error_message=msg)


@pytest.fixture(scope="module")
def wiremock() -> Iterator[str]:
    """
    Starts the WireMock Docker container, loads mappings from api.json,
    and yields the base URL for the mock server.
    """
    container = DockerContainer("wiremock/wiremock:3.5.2").with_exposed_ports(8080)
    container.start()
    time.sleep(10)

    host = container.get_container_host_ip()
    port = container.get_exposed_port(8080)
    # noinspection HttpUrlsUsage
    base_url = f"http://{host}:{port}"

    http = urllib3.PoolManager()
    mappings = json.loads(open("test/resources/api.json").read())["mappings"]
    for mapping in mappings:
        http.request(
            "POST",
            f"{base_url}/__admin/mappings",
            body=json.dumps(mapping),
            headers={"Content-Type": "application/json"},
        )

    yield base_url
    container.stop()


@pytest.fixture
def api_client(wiremock: str) -> DefaultApiClient:
    """
    Initializes DefaultApiClient with the mock OAuth host.
    """
    config = Configuration(NoAuthAuthenticator(host=wiremock, token="test-token"))  # noqa S106
    return DefaultApiClient(config)


def test_get_request(api_client: DefaultApiClient) -> None:
    """
    Test GET request is successful.
    """
    response = api_client.invoke_api(
        "testGetSuccess",
        "/users/123",
        "GET",
        {},
        {},
        {},
        None,
        SuccessModel,
        {200: SuccessModel},
    )
    assert isinstance(response, SuccessModel)


def test_post_request(api_client: DefaultApiClient) -> None:
    """
    Test POST request is successful.
    """
    response = api_client.invoke_api(
        "testPost",
        "/users",
        "POST",
        {},
        {},
        {},
        {"name": "John"},
        SuccessModel,
        {201: SuccessModel},
    )
    assert isinstance(response, SuccessModel)
    assert response.status == "created"


def test_sends_custom_headers(api_client: DefaultApiClient) -> None:
    """
    Test PUT request sends custom headers.
    """
    response = api_client.invoke_api(
        "testCustomHeaders",
        "/users/123",
        "PUT",
        {},
        {},
        {"X-Request-ID": "test-uuid-123"},
        {"name": "John"},
        SuccessModel,
        {200: SuccessModel},
    )
    assert isinstance(response, SuccessModel)


def test_delete_request(api_client: DefaultApiClient) -> None:
    """
    Test DELETE request returns void.
    """
    result = api_client.invoke_api(
        "testVoid",
        "/users/123",
        "DELETE",
        {},
        {},
        {},
        None,
        SuccessModel,
        {},
    )
    assert result is None


def test_api_client_error_response(api_client: DefaultApiClient) -> None:
    """
    Handles 404 Not Found error.
    """
    with pytest.raises(ApiError) as problem:
        api_client.invoke_api(
            "test404",
            "/users/notfound",
            "GET",
            {},
            {},
            {},
            None,
            SuccessModel,
            {},
        )
    assert problem.value.code == 404
    assert getattr(problem.value, "code", problem.value.code) == 404


def test_typed_client_error_response(api_client: DefaultApiClient) -> None:
    """
    Handles 400 Bad Request with a typed error model.
    """
    with pytest.raises(ApiError) as problem:
        api_client.invoke_api(
            "test400",
            "/users/bad",
            "POST",
            {},
            {},
            {},
            {"invalid": True},
            SuccessModel,
            {400: ErrorModel},
        )
    assert problem.value.code == 400
    assert isinstance(problem.value.response_body, ErrorModel)
    assert getattr(problem.value, "response_body", problem.value.response_body) is problem.value.response_body


def test_deserialization_failure(api_client: DefaultApiClient) -> None:
    """
    Handles successful response with malformed JSON.
    """
    with pytest.raises(RuntimeError):
        api_client.invoke_api(
            "testMalformed",
            "/malformed",
            "GET",
            {},
            {},
            {},
            None,
            SuccessModel,
            {200: SuccessModel},
        )
