# ruff: noqa
# mypy: ignore-errors
import datetime

import pytest

from zitadel_client.value_serializer import ValueSerializer


class TestValueSerializerPath:
    def test_null_returns_empty_string(self) -> None:
        assert ValueSerializer.serialize(None, "path", "string") == ""

    def test_string_returns_url_encoded_value(self) -> None:
        assert ValueSerializer.serialize("hello", "path", "string") == "hello"

    def test_string_with_spaces_is_url_encoded(self) -> None:
        assert (
            ValueSerializer.serialize("hello world", "path", "string")
            == "hello%20world"
        )

    def test_string_with_slash_is_url_encoded(self) -> None:
        assert ValueSerializer.serialize("a/b", "path", "string") == "a%2Fb"

    def test_integer_returns_string(self) -> None:
        assert ValueSerializer.serialize(42, "path", "integer") == "42"

    def test_boolean_true_returns_true(self) -> None:
        assert ValueSerializer.serialize(True, "path", "boolean") == "true"

    def test_boolean_false_returns_false(self) -> None:
        assert ValueSerializer.serialize(False, "path", "boolean") == "false"


class TestValueSerializerQuery:
    def test_null_returns_none(self) -> None:
        assert ValueSerializer.serialize(None, "query", "string") is None

    def test_string_returns_as_is(self) -> None:
        assert ValueSerializer.serialize("hello", "query", "string") == "hello"

    def test_integer_returns_string(self) -> None:
        assert ValueSerializer.serialize(42, "query", "integer") == "42"

    def test_boolean_true_returns_true(self) -> None:
        assert ValueSerializer.serialize(True, "query", "boolean") == "true"

    def test_boolean_false_returns_false(self) -> None:
        assert ValueSerializer.serialize(False, "query", "boolean") == "false"

    def test_array_joins_with_comma_by_default(self) -> None:
        assert ValueSerializer.serialize(["a", "b", "c"], "query", "array") == "a,b,c"

    def test_array_joins_with_comma_for_csv(self) -> None:
        assert (
            ValueSerializer.serialize(["a", "b", "c"], "query", "array", "csv")
            == "a,b,c"
        )

    def test_array_joins_with_space_for_ssv(self) -> None:
        assert (
            ValueSerializer.serialize(["a", "b", "c"], "query", "array", "ssv")
            == "a b c"
        )

    def test_array_joins_with_tab_for_tsv(self) -> None:
        assert (
            ValueSerializer.serialize(["a", "b", "c"], "query", "array", "tsv")
            == "a\tb\tc"
        )

    def test_array_joins_with_pipe_for_pipes(self) -> None:
        assert (
            ValueSerializer.serialize(["a", "b", "c"], "query", "array", "pipes")
            == "a|b|c"
        )

    def test_array_returns_list_for_multi(self) -> None:
        assert ValueSerializer.serialize(
            ["a", "b", "c"], "query", "array", "multi"
        ) == ["a", "b", "c"]

    def test_empty_array_returns_empty_string_for_csv(self) -> None:
        assert ValueSerializer.serialize([], "query", "array") == ""

    def test_empty_array_returns_empty_list_for_multi(self) -> None:
        assert ValueSerializer.serialize([], "query", "array", "multi") == []

    def test_single_element_array_returns_single_value(self) -> None:
        assert ValueSerializer.serialize(["a"], "query", "array") == "a"

    def test_array_of_integers_stringifies_elements(self) -> None:
        assert ValueSerializer.serialize([1, 2, 3], "query", "array") == "1,2,3"

    def test_array_of_booleans_stringifies_elements(self) -> None:
        assert (
            ValueSerializer.serialize([True, False], "query", "array") == "true,false"
        )


class TestValueSerializerHeader:
    def test_null_returns_empty_string(self) -> None:
        assert ValueSerializer.serialize(None, "header", "string") == ""

    def test_string_returns_as_is(self) -> None:
        assert ValueSerializer.serialize("hello", "header", "string") == "hello"

    def test_integer_returns_string(self) -> None:
        assert ValueSerializer.serialize(42, "header", "integer") == "42"

    def test_boolean_true_returns_true(self) -> None:
        assert ValueSerializer.serialize(True, "header", "boolean") == "true"

    def test_array_joins_with_comma(self) -> None:
        assert ValueSerializer.serialize(["a", "b", "c"], "header", "array") == "a,b,c"

    def test_empty_array_joins_to_empty_string(self) -> None:
        assert ValueSerializer.serialize([], "header", "array") == ""

    def test_array_of_integers_stringifies_and_joins(self) -> None:
        assert ValueSerializer.serialize([1, 2, 3], "header", "array") == "1,2,3"


class TestValueSerializerCookie:
    def test_string_returns_as_is(self) -> None:
        assert ValueSerializer.serialize("hello", "cookie", "string") == "hello"

    def test_null_returns_empty_string(self) -> None:
        assert ValueSerializer.serialize(None, "cookie", "string") == ""


class TestValueSerializerForm:
    def test_null_returns_empty_string(self) -> None:
        assert ValueSerializer.serialize(None, "form", "string") == ""

    def test_string_returns_as_is(self) -> None:
        assert ValueSerializer.serialize("hello", "form", "string") == "hello"

    def test_integer_returns_string(self) -> None:
        assert ValueSerializer.serialize(42, "form", "integer") == "42"

    def test_boolean_true_returns_true(self) -> None:
        assert ValueSerializer.serialize(True, "form", "boolean") == "true"

    def test_boolean_false_returns_false(self) -> None:
        assert ValueSerializer.serialize(False, "form", "boolean") == "false"


class TestMatrixStyle:
    def test_scalar_returns_semicolon_prefixed_name_value(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color", "blue", "path", "string", None, "matrix", True
            )
            == ";color=blue"
        )

    def test_array_with_explode_false_joins_with_comma(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color", ["blue", "black"], "path", "array", None, "matrix", False
            )
            == ";color=blue,black"
        )

    def test_array_with_explode_true_repeats_name(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color", ["blue", "black"], "path", "array", None, "matrix", True
            )
            == ";color=blue;color=black"
        )

    def test_null_returns_empty_string(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color", None, "path", "string", None, "matrix", True
            )
            == ""
        )


class TestLabelStyle:
    def test_scalar_returns_dot_prefixed_value(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color", "blue", "path", "string", None, "label", True
            )
            == ".blue"
        )

    def test_array_with_explode_false_joins_with_comma(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color", ["blue", "black"], "path", "array", None, "label", False
            )
            == ".blue,black"
        )

    def test_array_with_explode_true_joins_with_dot(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color", ["blue", "black"], "path", "array", None, "label", True
            )
            == ".blue.black"
        )

    def test_null_returns_empty_string(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color", None, "path", "string", None, "label", True
            )
            == ""
        )


class TestSpaceDelimitedStyle:
    def test_array_joins_with_space(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color",
                ["blue", "black"],
                "query",
                "array",
                None,
                "spaceDelimited",
                False,
            )
            == "blue black"
        )

    def test_scalar_returns_stringified_value(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color", "blue", "query", "string", None, "spaceDelimited", False
            )
            == "blue"
        )


class TestPipeDelimitedStyle:
    def test_array_joins_with_pipe(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color",
                ["blue", "black"],
                "query",
                "array",
                None,
                "pipeDelimited",
                False,
            )
            == "blue|black"
        )

    def test_scalar_returns_stringified_value(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color", "blue", "query", "string", None, "pipeDelimited", False
            )
            == "blue"
        )


class TestFormStyleWithExplode:
    def test_array_with_explode_false_joins_with_comma(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color", ["blue", "black"], "query", "array", None, "form", False
            )
            == "blue,black"
        )

    def test_array_with_explode_true_returns_list(self) -> None:
        assert ValueSerializer.serialize_styled(
            "color", ["blue", "black"], "query", "array", None, "form", True
        ) == ["blue", "black"]

    def test_scalar_with_explode_true_returns_string_not_list(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color", "blue", "query", "string", None, "form", True
            )
            == "blue"
        )

    def test_single_element_array_with_explode_true_returns_list(self) -> None:
        assert ValueSerializer.serialize_styled(
            "color", ["blue"], "query", "array", None, "form", True
        ) == ["blue"]

    def test_null_returns_none_for_query(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color", None, "query", "string", None, "form", True
            )
            is None
        )


class TestSimpleStyleBackwardCompatibility:
    def test_scalar_returns_stringified_value(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "id", "5", "path", "string", None, "simple", False
            )
            == "5"
        )

    def test_array_joins_with_comma(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "id", ["3", "4", "5"], "path", "array", None, "simple", False
            )
            == "3,4,5"
        )

    def test_null_returns_empty_string(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "id", None, "path", "string", None, "simple", True
            )
            == ""
        )

    def test_scalar_url_encodes_for_path(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "id", "hello world", "path", "string", None, "simple", False
            )
            == "hello%20world"
        )

    def test_path_serialization_is_final_and_must_not_be_double_encoded(self) -> None:
        # The api template substitutes ``str(serialize_styled(...))`` directly
        # into the path WITHOUT an additional ``quote()`` wrap. This guards
        # against the double-encoding regression where a space became
        # ``%2520`` and ``/`` became ``a%252Fb``. The serializer output here
        # is the FINAL wire value -- re-encoding it would be wrong.
        space = ValueSerializer.serialize_styled(
            "id", "a b", "path", "string", None, "simple", False
        )
        assert space == "a%20b"
        from urllib.parse import quote

        # A second encode (the removed outer wrap) would corrupt it.
        assert quote(str(space), safe="/;,=.~:!$&'()*+@") == "a%2520b"
        assert space != "a%2520b"

        slash = ValueSerializer.serialize_styled(
            "id", "a/b", "path", "string", None, "simple", False
        )
        assert slash == "a%2Fb"
        assert slash != "a%252Fb"


class TestNullStyleFallback:
    def test_path_with_null_style_behaves_like_simple(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "id", "5", "path", "string", None, None, False
            )
            == "5"
        )

    def test_empty_style_falls_back(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "id", "5", "path", "string", None, "", False
            )
            == "5"
        )


class TestDeepObjectSerialization:
    def test_basic_map_returns_bracketed_keys(self) -> None:
        result = ValueSerializer.serialize_deep_object(
            "filter", {"color": "blue", "size": "large"}
        )
        assert result["filter[color]"] == "blue"
        assert result["filter[size]"] == "large"

    def test_null_returns_empty_dict(self) -> None:
        result = ValueSerializer.serialize_deep_object("filter", None)
        assert result == {}


class TestPathEncodingParity:
    """Cross-language parity tests for path-segment percent-encoding.

    Every SDK must produce identical encoded strings for these inputs.
    """

    def test_ascii_safe_pass_through(self) -> None:
        assert ValueSerializer.serialize("abc123", "path", "string") == "abc123"

    def test_space_encoded(self) -> None:
        assert ValueSerializer.serialize("a b", "path", "string") == "a%20b"

    def test_slash_encoded(self) -> None:
        assert ValueSerializer.serialize("a/b", "path", "string") == "a%2Fb"

    def test_question_mark_encoded(self) -> None:
        assert ValueSerializer.serialize("a?b", "path", "string") == "a%3Fb"

    def test_hash_encoded(self) -> None:
        assert ValueSerializer.serialize("a#b", "path", "string") == "a%23b"

    def test_comma_preserved(self) -> None:
        assert ValueSerializer.serialize("a,b", "path", "string") == "a,b"

    def test_colon_preserved(self) -> None:
        assert ValueSerializer.serialize("a:b", "path", "string") == "a:b"

    def test_plus_preserved(self) -> None:
        assert ValueSerializer.serialize("a+b", "path", "string") == "a+b"

    def test_unicode_encoded(self) -> None:
        assert (
            ValueSerializer.serialize("日本", "path", "string") == "%E6%97%A5%E6%9C%AC"
        )

    def test_empty_string_preserved(self) -> None:
        assert ValueSerializer.serialize("", "path", "string") == ""

    def test_null_returns_empty(self) -> None:
        assert ValueSerializer.serialize(None, "path", "string") == ""

    def test_simple_style_encodes_value(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color", "a b", "path", "string", None, "simple", False
            )
            == "a%20b"
        )

    def test_simple_style_array_encodes_each_item(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color", ["a b", "c?d"], "path", "array", None, "simple", False
            )
            == "a%20b,c%3Fd"
        )

    def test_path_array_item_with_reserved_char_is_percent_encoded(self) -> None:
        # Gap W1 regression: every per-item path value in a styled array
        # must be percent-encoded BEFORE being joined with the structural
        # separator. Otherwise '/', '?', '#', space leak into the URL.
        items = ["a/b", "c"]
        assert (
            ValueSerializer.serialize_styled(
                "name", items, "path", "array", None, "simple", False
            )
            == "a%2Fb,c"
        )
        assert (
            ValueSerializer.serialize_styled(
                "name", items, "path", "array", None, "label", True
            )
            == ".a%2Fb.c"
        )
        assert (
            ValueSerializer.serialize_styled(
                "name", items, "path", "array", None, "matrix", False
            )
            == ";name=a%2Fb,c"
        )

    def test_matrix_style_encodes_value(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color", "a b", "path", "string", None, "matrix", False
            )
            == ";color=a%20b"
        )

    def test_label_style_encodes_value(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color", "a b", "path", "string", None, "label", False
            )
            == ".a%20b"
        )

    def test_query_location_not_path_encoded(self) -> None:
        assert (
            ValueSerializer.serialize_styled(
                "color", "a b", "query", "string", None, "form", False
            )
            == "a b"
        )

    def test_empty_string_path_param_raises(self) -> None:
        # Gap W — empty-string path values silently produce malformed
        # URLs like `/pet//details`; reject at serialization time so
        # callers see the real error rather than a downstream 404.
        with pytest.raises(ValueError):
            ValueSerializer.serialize_styled(
                "id", "", "path", "string", None, "simple", False
            )


class TestValueSerializerFormatDatePath:
    """N3/W3 parity: ``format: date`` path parameters must emit a date-only
    string (YYYY-MM-DD), not a full ISO datetime. Python models
    ``format: date`` as ``datetime.date``, which the value serializer
    formats via ``isoformat()``.
    """

    def test_date_in_path_returns_yyyy_mm_dd(self) -> None:
        date = datetime.date(2024, 1, 15)
        assert ValueSerializer.serialize(date, "path", "string") == "2024-01-15"

    def test_date_via_serialize_styled_simple_returns_yyyy_mm_dd(self) -> None:
        date = datetime.date(2024, 1, 15)
        assert (
            ValueSerializer.serialize_styled(
                "since", date, "path", "string", None, "simple", False
            )
            == "2024-01-15"
        )

    def test_date_at_year_boundary_emits_date_only(self) -> None:
        # UTC/midnight edge: a date on the year boundary must serialize as a
        # bare YYYY-MM-DD with no time/offset suffix, matching the
        # stringifyDate UTC behaviour of Go/Node/Swift/Dart.
        date = datetime.date(2024, 12, 31)
        assert ValueSerializer.serialize(date, "path", "string") == "2024-12-31"
