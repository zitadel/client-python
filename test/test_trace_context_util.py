# ruff: noqa
# mypy: ignore-errors
"""Unit tests for TraceContextUtil."""

import pytest

from zitadel_client.trace_context_util import inject_trace_context


class TestInjectTraceContext:
    """Tests for inject_trace_context function."""

    def test_no_op_without_tracer(self) -> None:
        headers: dict[str, str] = {}
        inject_trace_context(headers)

    def test_empty_headers_do_not_cause_exception(self) -> None:
        headers: dict[str, str] = {}
        inject_trace_context(headers)
        assert len(headers) == 0

    def test_does_not_inject_traceparent_without_otel(self) -> None:
        headers: dict[str, str] = {}
        inject_trace_context(headers)
        assert "traceparent" not in headers

    def test_does_not_inject_tracestate_without_otel(self) -> None:
        headers: dict[str, str] = {}
        inject_trace_context(headers)
        assert "tracestate" not in headers

    def test_preserves_authorization_header(self) -> None:
        headers: dict[str, str] = {"Authorization": "Bearer token123"}
        inject_trace_context(headers)
        assert headers["Authorization"] == "Bearer token123"

    def test_preserves_content_type_header(self) -> None:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        inject_trace_context(headers)
        assert headers["Content-Type"] == "application/json"

    def test_preserves_x_request_id_header(self) -> None:
        headers: dict[str, str] = {"X-Request-ID": "req-12345"}
        inject_trace_context(headers)
        assert headers["X-Request-ID"] == "req-12345"

    def test_preserves_all_existing_headers(self) -> None:
        headers: dict[str, str] = {
            "Authorization": "Bearer token",
            "Content-Type": "application/json",
            "X-Request-ID": "abc-123",
        }
        inject_trace_context(headers)
        assert len(headers) == 3
        assert headers["Authorization"] == "Bearer token"
        assert headers["Content-Type"] == "application/json"
        assert headers["X-Request-ID"] == "abc-123"

    @pytest.mark.skip(
        reason="no ambient tracer like .NET Activity.Current; active-span injection "
        "requires a fully configured OpenTelemetry SDK out of scope for this unit test"
    )
    def test_injects_traceparent_when_span_active(self) -> None:
        # .NET-specific scenario: relies on Activity.Current ambient context.
        ...

    @pytest.mark.skip(
        reason="no ambient tracer like .NET Activity.Current; tracestate-present "
        "requires a fully configured OpenTelemetry SDK out of scope for this unit test"
    )
    def test_includes_tracestate_when_present(self) -> None:
        # .NET-specific scenario: relies on Activity.Current ambient context.
        ...

    @pytest.mark.skip(
        reason="no ambient tracer like .NET Activity.Current; empty-tracestate "
        "requires a fully configured OpenTelemetry SDK out of scope here"
    )
    def test_omits_tracestate_when_empty(self) -> None:
        # .NET-specific scenario: relies on Activity.Current ambient context.
        ...

    @pytest.mark.skip(
        reason="no ambient tracer like .NET Activity.Current; trace-flags formatting "
        "requires a fully configured OpenTelemetry SDK out of scope for this unit test"
    )
    def test_formats_trace_flags_correctly(self) -> None:
        # .NET-specific scenario: relies on Activity.Current ambient context.
        ...
