# ruff: noqa
# mypy: ignore-errors
import pytest
from types import MappingProxyType

from zitadel_client.transport_options import TransportOptions


class TestTransportOptions:
    def test_verify_ssl_defaults_to_true(self) -> None:
        opts = TransportOptions.builder().build()
        assert opts.verify_ssl is True

    def test_ca_cert_path_defaults_to_none(self) -> None:
        opts = TransportOptions.builder().build()
        assert opts.ca_cert_path is None

    def test_proxy_defaults_to_none(self) -> None:
        opts = TransportOptions.builder().build()
        assert opts.proxy is None

    def test_timeout_defaults_to_ten_seconds(self) -> None:
        opts = TransportOptions.builder().build()
        assert opts.timeout == 10000

    def test_follow_redirects_defaults_to_true(self) -> None:
        opts = TransportOptions.builder().build()
        assert opts.follow_redirects is True

    def test_max_redirects_defaults_to_none(self) -> None:
        opts = TransportOptions.builder().build()
        assert opts.max_redirects is None

    def test_user_agent_defaults_to_non_empty_string(self) -> None:
        opts = TransportOptions.builder().build()
        assert opts.user_agent is not None
        assert len(opts.user_agent) > 0

    def test_default_headers_defaults_to_empty(self) -> None:
        opts = TransportOptions.builder().build()
        assert len(opts.default_headers) == 0

    def test_inject_request_id_defaults_to_false(self) -> None:
        opts = TransportOptions.builder().build()
        assert opts.inject_request_id is False

    def test_builder_sets_all_fields(self) -> None:
        opts = (
            TransportOptions.builder()
            .verify_ssl(False)
            .ca_cert_path("/path/to/ca.pem")
            .proxy("http://proxy:8080")
            .timeout(5000)
            .follow_redirects(False)
            .max_redirects(3)
            .user_agent("TestAgent/1.0")
            .default_header("X-Custom", "value")
            .inject_request_id(True)
            .build()
        )

        assert opts.verify_ssl is False
        assert opts.ca_cert_path == "/path/to/ca.pem"
        assert opts.proxy == "http://proxy:8080"
        assert opts.timeout == 5000
        assert opts.follow_redirects is False
        assert opts.max_redirects == 3
        assert opts.user_agent == "TestAgent/1.0"
        assert opts.default_headers["X-Custom"] == "value"
        assert opts.inject_request_id is True

    def test_follow_redirects_defaults_to_true_with_null_max_redirects(self) -> None:
        opts = TransportOptions.builder().follow_redirects(True).build()

        assert opts.follow_redirects is True
        assert opts.max_redirects is None

    def test_invalid_proxy_url_throws_exception(self) -> None:
        with pytest.raises(ValueError):
            TransportOptions.builder().proxy("not-a-url").build()

    def test_null_proxy_url_is_accepted(self) -> None:
        opts = TransportOptions.builder().proxy(None).build()
        assert opts.proxy is None

    def test_builder_methods_return_same_instance(self) -> None:
        builder = TransportOptions.builder()

        assert builder.verify_ssl(True) is builder
        assert builder.ca_cert_path(None) is builder
        assert builder.proxy(None) is builder
        assert builder.timeout(None) is builder
        assert builder.follow_redirects(True) is builder
        assert builder.max_redirects(None) is builder
        assert builder.user_agent(None) is builder
        assert builder.default_header("X-Key", "val") is builder
        assert builder.default_headers({}) is builder
        assert builder.inject_request_id(False) is builder

    def test_accumulates_headers_from_default_header_calls(self) -> None:
        opts = (
            TransportOptions.builder()
            .default_header("X-First", "one")
            .default_header("X-Second", "two")
            .build()
        )

        assert len(opts.default_headers) == 2
        assert opts.default_headers["X-First"] == "one"
        assert opts.default_headers["X-Second"] == "two"

    def test_merges_headers_from_default_headers_call(self) -> None:
        opts = (
            TransportOptions.builder()
            .default_header("X-First", "one")
            .default_headers({"X-Second": "two", "X-Third": "three"})
            .build()
        )

        assert len(opts.default_headers) == 3
        assert opts.default_headers["X-First"] == "one"
        assert opts.default_headers["X-Second"] == "two"
        assert opts.default_headers["X-Third"] == "three"

    def test_modifying_source_map_does_not_affect_built_options(self) -> None:
        headers = {"X-Original": "original"}

        opts = TransportOptions.builder().default_headers(headers).build()

        headers["X-Added"] = "added"

        assert len(opts.default_headers) == 1
        assert opts.default_headers["X-Original"] == "original"
        assert "X-Added" not in opts.default_headers
        assert isinstance(opts.default_headers, MappingProxyType)

    def test_builder_produces_independent_instances(self) -> None:
        builder = TransportOptions.builder().verify_ssl(False)
        first = builder.build()
        second = builder.build()

        assert first.verify_ssl == second.verify_ssl
        assert first is not second

    # TimeoutConfigTests

    def test_timeout_defaults_to_ten_seconds_in_timeout_group(self) -> None:
        # Default TransportOptions has a 10s end-to-end timeout.
        opts = TransportOptions.builder().build()
        assert opts.timeout == 10000

    def test_timeout_can_be_explicitly_disabled(self) -> None:
        opts = TransportOptions.builder().timeout(None).build()
        assert opts.timeout is None

    def test_setting_timeout_is_accessible(self) -> None:
        opts = TransportOptions.builder().timeout(5000).build()
        assert opts.timeout == 5000

    def test_timeout_field_is_named_timeout(self) -> None:
        # Verify via the attribute that the field is named 'timeout'
        # (not e.g. 'connection_timeout' or 'open_timeout').
        opts = TransportOptions.builder().timeout(1000).build()
        assert opts.timeout is not None
        assert opts.timeout == 1000

    # ProxyConfigTests

    def test_proxy_url_is_preserved_on_read_back(self) -> None:
        opts = TransportOptions.builder().proxy("http://proxy.example.com:8080").build()
        assert opts.proxy == "http://proxy.example.com:8080"

    def test_setting_proxy_is_supported_on_all_platforms(self) -> None:
        # Proxy configuration must not raise on any platform.
        opts = TransportOptions.builder().proxy("http://proxy.example.com:8080").build()
        assert opts.proxy == "http://proxy.example.com:8080"
