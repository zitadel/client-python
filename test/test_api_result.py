# ruff: noqa
# mypy: ignore-errors
import pytest

from zitadel_client.api_result import ApiResult


class TestApiResult:
    def test_carries_data_status_code_headers_and_raw_body(self) -> None:
        result = ApiResult(
            status_code=200,
            data={"id": 1},
            raw_body='{"id": 1}',
            headers={"Content-Type": "application/json"},
        )

        assert result.status_code == 200
        assert result.data == {"id": 1}
        assert result.raw_body == '{"id": 1}'
        assert result.headers == {"Content-Type": "application/json"}

    def test_data_may_be_none_for_empty_response(self) -> None:
        # A 204 No Content carries no deserialized payload, but raw_body is
        # always populated (an empty string when the server sent no body).
        result = ApiResult(status_code=204, data=None, raw_body="", headers={})

        assert result.status_code == 204
        assert result.data is None
        assert result.raw_body == ""
        assert result.headers == {}

    def test_is_frozen(self) -> None:
        # ApiResult is an immutable @dataclass(frozen=True); attribute
        # assignment must raise.
        result = ApiResult(status_code=200, data=None, raw_body="", headers={})

        with pytest.raises(Exception):
            result.status_code = 500
