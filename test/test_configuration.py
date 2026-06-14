# ruff: noqa
# mypy: ignore-errors
from types import MappingProxyType

from zitadel_client.configuration import Configuration, ConfigurationBuilder
from zitadel_client.server_configuration import ServerConfiguration, ServerVariable


class TestConfigurationDefaults:
    def test_default_constructor_uses_spec_base_url(self) -> None:
        config = Configuration()

        assert config.base_url == "https://zitadel.com"
        assert len(config.default_headers) == 0

    def test_builder_produces_correct_defaults(self) -> None:
        config = Configuration.builder().build()

        assert config.base_url == "https://zitadel.com"
        assert len(config.default_headers) == 0

    def test_builder_returns_configuration_builder_instance(self) -> None:
        builder = Configuration.builder()

        assert isinstance(builder, ConfigurationBuilder)


class TestConfigurationBuilder:
    def test_builder_sets_base_url(self) -> None:
        config = Configuration.builder().base_url("https://custom.example.com").build()

        assert config.base_url == "https://custom.example.com"

    def test_builder_sets_single_default_header(self) -> None:
        config = (
            Configuration.builder()
            .default_header("Authorization", "Bearer token123")
            .build()
        )

        assert config.default_headers["Authorization"] == "Bearer token123"

    def test_builder_sets_multiple_default_headers(self) -> None:
        config = (
            Configuration.builder()
            .default_headers(
                {
                    "Authorization": "Bearer token123",
                    "X-Custom": "value",
                }
            )
            .build()
        )

        assert config.default_headers["Authorization"] == "Bearer token123"
        assert config.default_headers["X-Custom"] == "value"

    def test_builder_accumulates_headers(self) -> None:
        config = (
            Configuration.builder()
            .default_header("X-First", "one")
            .default_header("X-Second", "two")
            .default_headers({"X-Third": "three"})
            .build()
        )

        assert len(config.default_headers) == 3
        assert config.default_headers["X-First"] == "one"
        assert config.default_headers["X-Second"] == "two"
        assert config.default_headers["X-Third"] == "three"

    def test_builder_merges_single_and_bulk_headers(self) -> None:
        config = (
            Configuration.builder()
            .default_header("X-First", "one")
            .default_headers({"X-Second": "two"})
            .default_header("X-Third", "three")
            .build()
        )

        assert len(config.default_headers) == 3
        assert config.default_headers["X-First"] == "one"
        assert config.default_headers["X-Second"] == "two"
        assert config.default_headers["X-Third"] == "three"

    def test_builder_produces_independent_instances(self) -> None:
        builder = Configuration.builder().base_url("https://example.com")
        first = builder.build()
        second = builder.build()

        assert first is not second
        assert first.base_url == second.base_url

    def test_builder_sets_all_fields(self) -> None:
        config = (
            Configuration.builder()
            .base_url("https://api.example.com")
            .default_header("Authorization", "Bearer token")
            .default_headers({"X-Custom": "value"})
            .build()
        )

        assert config.base_url == "https://api.example.com"
        assert config.default_headers["Authorization"] == "Bearer token"
        assert config.default_headers["X-Custom"] == "value"

    def test_builder_is_fluent(self) -> None:
        builder = Configuration.builder()

        assert builder is builder.base_url("https://example.com")
        assert builder is builder.default_header("X-Key", "value")
        assert builder is builder.default_headers({"X-Other": "val"})

        server = ServerConfiguration(url_template="https://example.com")
        assert builder is builder.server(server)


class TestConfigurationServerResolution:
    def test_builder_server_resolves_url(self) -> None:
        server = ServerConfiguration(
            url_template="https://{env}.example.com/api/{version}",
            description="Test server",
            variables={
                "env": ServerVariable(
                    default_value="api",
                    enum_values=["api", "staging"],
                ),
                "version": ServerVariable(
                    default_value="v3",
                    enum_values=["v2", "v3"],
                ),
            },
        )

        config = Configuration.builder().server(server).build()

        assert config.base_url == "https://api.example.com/api/v3"

    def test_builder_server_with_variable_overrides(self) -> None:
        server = ServerConfiguration(
            url_template="https://{env}.example.com/api/{version}",
            variables={
                "env": ServerVariable(
                    default_value="api",
                    enum_values=["api", "staging"],
                ),
                "version": ServerVariable(
                    default_value="v3",
                    enum_values=["v2", "v3"],
                ),
            },
        )

        config = (
            Configuration.builder()
            .server(server, {"env": "staging", "version": "v2"})
            .build()
        )

        assert config.base_url == "https://staging.example.com/api/v2"

    def test_builder_base_url_overrides_server(self) -> None:
        server = ServerConfiguration(url_template="https://api.example.com")

        config = (
            Configuration.builder()
            .server(server)
            .base_url("https://override.example.com")
            .build()
        )

        assert config.base_url == "https://override.example.com"


class TestConfigurationSingleton:
    def teardown_method(self) -> None:
        Configuration.set_default(None)

    def test_get_default_returns_instance(self) -> None:
        config = Configuration.get_default()

        assert isinstance(config, Configuration)
        assert config.base_url == "https://zitadel.com"

    def test_get_default_returns_same_instance(self) -> None:
        first = Configuration.get_default()
        second = Configuration.get_default()

        assert first is second

    def test_set_default_changes_default(self) -> None:
        custom = Configuration.builder().base_url("https://custom.example.com").build()

        Configuration.set_default(custom)

        assert Configuration.get_default() is custom
        assert Configuration.get_default().base_url == "https://custom.example.com"


class TestConfigurationImmutability:
    def test_default_headers_is_immutable(self) -> None:
        config = Configuration.builder().default_header("X-Key", "value").build()

        assert isinstance(config.default_headers, MappingProxyType)
        assert config.default_headers["X-Key"] == "value"
