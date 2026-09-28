import pytest

from zitadel_client.errors import ZitadelException
from zitadel_client.server_configuration import ServerConfiguration, ServerVariable


class TestServerConfiguration:
    def test_resolves_url_template_using_default_variable_values(self) -> None:
        config = ServerConfiguration(
            url_template="https://{env}.api.example.com/v{version}",
            description="primary server",
            variables={
                "env": ServerVariable(
                    default_value="prod", enum_values=["prod", "staging"]
                ),
                "version": ServerVariable(default_value="1"),
            },
        )

        assert config.get_url() == "https://prod.api.example.com/v1"

    def test_applies_overrides_and_falls_back_to_defaults_for_unset_variables(
        self,
    ) -> None:
        # "env" is overridden, "version" is left to its default — the resolved
        # URL must mix both.
        config = ServerConfiguration(
            url_template="https://{env}.api.example.com/v{version}",
            variables={
                "env": ServerVariable(
                    default_value="prod", enum_values=["prod", "staging"]
                ),
                "version": ServerVariable(default_value="1"),
            },
        )

        assert (
            config.get_url({"env": "staging"}) == "https://staging.api.example.com/v1"
        )

    def test_exposes_raw_url_template_and_description(self) -> None:
        config = ServerConfiguration(
            url_template="https://{env}.api.example.com",
            description="primary server",
            variables={"env": ServerVariable(default_value="prod")},
        )

        assert config.url_template == "https://{env}.api.example.com"
        assert config.description == "primary server"

    def test_rejects_override_value_outside_the_variable_enum(self) -> None:
        # server-variable-enum-validation: an override that is not in the
        # variable's enum is rejected at resolution time.
        config = ServerConfiguration(
            url_template="https://{env}.api.example.com",
            variables={
                "env": ServerVariable(
                    default_value="prod", enum_values=["prod", "staging"]
                ),
            },
        )

        with pytest.raises(ValueError) as exc_info:
            config.get_url({"env": "dev"})
        assert type(exc_info.value) is ValueError
        assert not isinstance(exc_info.value, ZitadelException)

    def test_template_without_variables_is_returned_verbatim(self) -> None:
        config = ServerConfiguration(url_template="https://api.example.com")

        assert config.get_url() == "https://api.example.com"
