# ruff: noqa
# mypy: ignore-errors
"""
Swagger Petstore - OpenAPI 3.0

Unit tests for HeaderSelector.

These tests verify that the Accept header is built by joining the acceptable
MIME types in their original declaration order, with no quality weights.
"""

import pytest
from typing import Any
from zitadel_client.header_selector import HeaderSelector


class TestIsJsonMime:
    """Tests for is_json_mime method."""

    @pytest.fixture
    def header_selector(self) -> HeaderSelector:
        return HeaderSelector()

    def test_should_return_true_for_application_json(
        self, header_selector: Any
    ) -> None:
        assert header_selector.is_json_mime("application/json") is True

    def test_should_return_true_for_application_json_with_charset(
        self, header_selector: Any
    ) -> None:
        assert header_selector.is_json_mime("application/json; charset=UTF-8") is True

    def test_should_return_true_for_uppercase_application_json(
        self, header_selector: Any
    ) -> None:
        assert header_selector.is_json_mime("APPLICATION/JSON") is True

    def test_should_return_true_for_vendor_json_types(
        self, header_selector: Any
    ) -> None:
        assert header_selector.is_json_mime("application/vnd.api+json") is True
        assert header_selector.is_json_mime("application/vnd.company+json") is True
        assert header_selector.is_json_mime("application/hal+json") is True

    def test_should_return_false_for_text_html(self, header_selector: Any) -> None:
        assert header_selector.is_json_mime("text/html") is False

    def test_should_return_false_for_application_xml(
        self, header_selector: Any
    ) -> None:
        assert header_selector.is_json_mime("application/xml") is False

    def test_should_return_false_for_none(self, header_selector: Any) -> None:
        assert header_selector.is_json_mime(None) is False

    def test_should_return_false_for_empty_string(self, header_selector: Any) -> None:
        assert header_selector.is_json_mime("") is False


class TestSelectAcceptHeader:
    """Tests for _select_accept_header method."""

    @pytest.fixture
    def header_selector(self) -> HeaderSelector:
        return HeaderSelector()

    def test_should_return_none_for_none_input(self, header_selector: Any) -> None:
        assert header_selector._select_accept_header(None) is None

    def test_should_return_none_for_empty_list(self, header_selector: Any) -> None:
        assert header_selector._select_accept_header([]) is None

    def test_should_return_none_when_all_entries_filtered_out(
        self, header_selector: Any
    ) -> None:
        assert header_selector._select_accept_header(["", None]) is None

    def test_should_return_single_accept_as_is(self, header_selector: Any) -> None:
        assert (
            header_selector._select_accept_header(["application/json"])
            == "application/json"
        )

    def test_should_return_single_non_json_accept_as_is(
        self, header_selector: Any
    ) -> None:
        assert header_selector._select_accept_header(["text/html"]) == "text/html"

    def test_should_join_in_declaration_order(self, header_selector: Any) -> None:
        result = header_selector._select_accept_header(
            ["image/jpeg", "image/png", "application/json"]
        )
        assert result == "image/jpeg, image/png, application/json"

    def test_should_not_reorder_or_prioritize_json(self, header_selector: Any) -> None:
        result = header_selector._select_accept_header(
            ["text/html", "application/json"]
        )
        # No JSON-first reordering, no quality weights.
        assert result == "text/html, application/json"

    def test_should_filter_out_empty_entries_and_join_rest(
        self, header_selector: Any
    ) -> None:
        result = header_selector._select_accept_header(["", "application/json", None])
        assert result == "application/json"

    def test_should_not_add_quality_weights(self, header_selector: Any) -> None:
        result = header_selector._select_accept_header(
            ["text/html", "text/plain", "application/json"]
        )
        assert "q=" not in result
        assert result == "text/html, text/plain, application/json"


class TestSelectHeaders:
    """Tests for select_headers method."""

    @pytest.fixture
    def header_selector(self) -> HeaderSelector:
        return HeaderSelector()

    def test_should_set_accept_header_when_accepts_provided(
        self, header_selector: Any
    ) -> None:
        headers = header_selector.select_headers(
            ["application/json"], "application/json", False
        )
        assert headers.get("Accept") == "application/json"

    def test_should_not_set_accept_header_when_accepts_empty(
        self, header_selector: Any
    ) -> None:
        headers = header_selector.select_headers([], "application/json", False)
        assert headers.get("Accept") is None

    def test_should_set_content_type_header_when_not_multipart(
        self, header_selector: Any
    ) -> None:
        headers = header_selector.select_headers(
            ["application/json"], "application/json", False
        )
        assert headers.get("Content-Type") == "application/json"

    def test_should_not_set_content_type_header_when_multipart(
        self, header_selector: Any
    ) -> None:
        headers = header_selector.select_headers(
            ["application/json"], "application/json", True
        )
        assert headers.get("Content-Type") is None

    def test_should_default_content_type_to_application_json_when_empty(
        self, header_selector: Any
    ) -> None:
        headers = header_selector.select_headers(["application/json"], "", False)
        assert headers.get("Content-Type") == "application/json"

    def test_should_default_content_type_to_application_json_when_none(
        self, header_selector: Any
    ) -> None:
        headers = header_selector.select_headers(["application/json"], None, False)
        assert headers.get("Content-Type") == "application/json"
