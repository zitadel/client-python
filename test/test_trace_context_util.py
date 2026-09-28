"""Unit tests for TraceContextUtil."""

import re

from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.sampling import ALWAYS_OFF, ALWAYS_ON, Sampler
from opentelemetry.trace import (
    NonRecordingSpan,
    SpanContext,
    TraceFlags,
    TraceState,
    Tracer,
)

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

    def test_injects_traceparent_when_span_active(self) -> None:
        tracer, exporter = _sdk_tracer()
        headers: dict[str, str] = {}
        with tracer.start_as_current_span("request") as span:
            inject_trace_context(headers)
            ctx = span.get_span_context()
        assert (
            headers["traceparent"]
            == f"00-{ctx.trace_id:032x}-{ctx.span_id:016x}-{ctx.trace_flags:02x}"
        )
        assert [s.name for s in exporter.get_finished_spans()] == ["request"]

    def test_includes_tracestate_when_present(self) -> None:
        tracer, _ = _sdk_tracer()
        parent = _remote_parent(TraceState([("vendor", "value")]))
        headers: dict[str, str] = {}
        with tracer.start_as_current_span("request", context=parent):
            inject_trace_context(headers)
        assert headers["tracestate"] == "vendor=value"

    def test_omits_tracestate_when_empty(self) -> None:
        tracer, _ = _sdk_tracer()
        headers: dict[str, str] = {}
        with tracer.start_as_current_span("request"):
            inject_trace_context(headers)
        assert "traceparent" in headers
        assert "tracestate" not in headers

    def test_formats_trace_flags_correctly(self) -> None:
        sampled, _ = _sdk_tracer()
        unsampled, _ = _sdk_tracer(ALWAYS_OFF)
        sampled_headers: dict[str, str] = {}
        unsampled_headers: dict[str, str] = {}
        with sampled.start_as_current_span("sampled"):
            inject_trace_context(sampled_headers)
        with unsampled.start_as_current_span("unsampled"):
            inject_trace_context(unsampled_headers)
        sampled_flags = sampled_headers["traceparent"].split("-")[3]
        unsampled_flags = unsampled_headers["traceparent"].split("-")[3]
        # Two lowercase hex digits; the low bit is the sampled flag.
        assert re.fullmatch("[0-9a-f]{2}", sampled_flags)
        assert re.fullmatch("[0-9a-f]{2}", unsampled_flags)
        assert int(sampled_flags, 16) & TraceFlags.SAMPLED == TraceFlags.SAMPLED
        assert int(unsampled_flags, 16) & TraceFlags.SAMPLED == 0


def _sdk_tracer(sampler: Sampler = ALWAYS_ON) -> tuple[Tracer, InMemorySpanExporter]:
    """A tracer from a real OpenTelemetry SDK provider that records every
    finished span in memory, so the test controls the active span."""
    exporter = InMemorySpanExporter()
    provider = TracerProvider(sampler=sampler)
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return provider.get_tracer("trace-context-test"), exporter


def _remote_parent(trace_state: TraceState) -> Context:
    """A context whose active span is a sampled remote parent carrying the
    given tracestate, which a child span inherits."""
    parent = SpanContext(
        trace_id=0x0AF7651916CD43DD8448EB211C80319C,
        span_id=0xB7AD6B7169203331,
        is_remote=True,
        trace_flags=TraceFlags(TraceFlags.SAMPLED),
        trace_state=trace_state,
    )
    return trace.set_span_in_context(NonRecordingSpan(parent))
