from zitadel_client.server_configuration import ServerVariable


class TestServerVariable:
    def test_exposes_default_value_when_no_override_is_applied(self) -> None:
        # The default value is what ServerConfiguration falls back to when a
        # variable is left unset, so it must be carried through verbatim.
        var = ServerVariable(default_value="v1", description="API version")

        assert var.default_value == "v1"
        assert var.description == "API version"

    def test_omitted_enum_values_becomes_empty_list_meaning_any_value_allowed(
        self,
    ) -> None:
        var = ServerVariable(default_value="prod")

        assert var.enum_values == []
        assert var.description is None

    def test_enum_values_are_exposed_for_validation(self) -> None:
        # ServerConfiguration validates overrides against this set, so the
        # enum list must surface exactly the allowed values.
        var = ServerVariable(
            default_value="prod",
            description="deployment environment",
            enum_values=["prod", "staging"],
        )

        assert var.enum_values == ["prod", "staging"]
        assert "prod" in var.enum_values
        assert "staging" in var.enum_values

    def test_enum_does_not_contain_a_value_outside_the_allowed_set(self) -> None:
        # An out-of-set value (e.g. "dev") is absent from the enum, which is
        # what drives ServerConfiguration to reject it.
        var = ServerVariable(default_value="prod", enum_values=["prod", "staging"])

        assert "dev" not in var.enum_values
