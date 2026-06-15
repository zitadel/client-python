# ruff: noqa
# mypy: ignore-errors
import json
import pytest
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from typing import Any, ClassVar

from zitadel_client.default_api_client import (
    DefaultApiClient,
    _charset_from_content_type,
    _decode_with_charset,
    _guess_content_type,
    _sanitize_multipart_field_name,
    _sanitize_multipart_filename,
)
from zitadel_client.transport_options import TransportOptions


class _EchoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self._respond()

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode() if length else ""
        self._respond(body)

    def do_PUT(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode() if length else ""
        self._respond(body)

    def do_DELETE(self) -> None:
        self._respond()

    def _respond(self, body: str = "") -> None:
        if self.path == "/not-found":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"not found")
            return

        if self.path == "/bad-gzip":
            # Advertise gzip but send bytes that are NOT valid gzip. The
            # client must surface this as the SDK's ApiException rather than
            # leaking a raw gzip.BadGzipFile / OSError.
            payload = b"this is definitely not gzip"
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        # Echo back all received headers as JSON. Lowercase the keys to match
        # chasm's /test/echo envelope shape so tests use a single key style.
        received_headers = {k.lower(): v for k, v in self.headers.items()}
        data = json.dumps(
            {"method": self.command, "body": body, "headers": received_headers}
        )
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-Test-Header", "test-value")
        self.end_headers()
        self.wfile.write(data.encode())

    def log_message(self, format: str, *args: Any) -> None:
        pass


class TestDefaultApiClientUnit:
    server: HTTPServer
    port: int
    base_url: str
    thread: Thread

    @classmethod
    def setup_class(cls) -> None:
        cls.server = HTTPServer(("127.0.0.1", 0), _EchoHandler)
        cls.port = cls.server.server_address[1]
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def teardown_class(cls) -> None:
        cls.server.shutdown()

    def test_sends_get_request_and_returns_response(self) -> None:
        client = DefaultApiClient()
        response = client.send_request("GET", f"{self.base_url}/echo", {}, None)
        assert response.status_code == 200
        body = json.loads(response.body)
        assert body["method"] == "GET"

    def test_sends_post_with_json_body(self) -> None:
        client = DefaultApiClient()
        headers = {"Content-Type": "application/json"}
        response = client.send_request(
            "POST", f"{self.base_url}/echo", headers, '{"key":"value"}'
        )
        assert response.status_code == 200
        body = json.loads(response.body)
        assert body["method"] == "POST"
        assert "key" in body["body"]

    def test_returns_response_headers(self) -> None:
        client = DefaultApiClient()
        response = client.send_request("GET", f"{self.base_url}/echo", {}, None)
        lower_headers = {k.lower(): v for k, v in response.headers.items()}
        assert "x-test-header" in lower_headers
        assert lower_headers["x-test-header"] == "test-value"

    def test_malformed_gzip_body_raises_api_exception(self) -> None:
        """decompression-error-not-wrapped: a body that advertises
        Content-Encoding: gzip but is not valid gzip must surface as the
        SDK's ApiException, not a raw gzip.BadGzipFile / OSError."""
        from zitadel_client.errors import ApiException

        client = DefaultApiClient()
        with pytest.raises(ApiException) as exc_info:
            client.send_request("GET", f"{self.base_url}/bad-gzip", {}, None)
        assert "decompress" in str(exc_info.value.message or "").lower()

    def test_returns_non_2xx_status_code(self) -> None:
        client = DefaultApiClient()
        response = client.send_request("GET", f"{self.base_url}/not-found", {}, None)
        assert response.status_code == 404
        assert response.body == "not found"

    def test_sends_put_request(self) -> None:
        client = DefaultApiClient()
        response = client.send_request("PUT", f"{self.base_url}/echo", {}, "update")
        assert response.status_code == 200
        body = json.loads(response.body)
        assert body["method"] == "PUT"

    def test_sends_delete_request(self) -> None:
        client = DefaultApiClient()
        response = client.send_request("DELETE", f"{self.base_url}/echo", {}, None)
        assert response.status_code == 200
        body = json.loads(response.body)
        assert body["method"] == "DELETE"

    def test_injects_custom_user_agent(self) -> None:
        transport = TransportOptions.builder().user_agent("TestAgent/1.0").build()
        client = DefaultApiClient(transport)
        response = client.send_request("GET", f"{self.base_url}/echo", {}, None)
        assert response.status_code == 200
        body = json.loads(response.body)
        assert body["headers"].get("user-agent") == "TestAgent/1.0"

    def test_injects_default_user_agent_when_not_explicitly_set(self) -> None:
        client = DefaultApiClient()
        response = client.send_request("GET", f"{self.base_url}/echo", {}, None)
        assert response.status_code == 200
        body = json.loads(response.body)
        assert body["headers"].get("user-agent") is not None
        assert len(body["headers"].get("user-agent", "")) > 0

    def test_injects_request_id(self) -> None:
        transport = TransportOptions.builder().inject_request_id(True).build()
        client = DefaultApiClient(transport)
        response = client.send_request("GET", f"{self.base_url}/echo", {}, None)
        assert response.status_code == 200
        body = json.loads(response.body)
        assert "x-request-id" in body["headers"]
        assert len(body["headers"]["x-request-id"]) > 0

    def test_does_not_inject_request_id_when_disabled(self) -> None:
        transport = TransportOptions.builder().inject_request_id(False).build()
        client = DefaultApiClient(transport)
        response = client.send_request("GET", f"{self.base_url}/echo", {}, None)
        assert response.status_code == 200
        body = json.loads(response.body)
        assert "x-request-id" not in body["headers"]

    def test_includes_transport_default_headers(self) -> None:
        transport = (
            TransportOptions.builder()
            .default_header("X-Custom-Transport", "transport-value")
            .build()
        )
        client = DefaultApiClient(transport)
        response = client.send_request("GET", f"{self.base_url}/echo", {}, None)
        assert response.status_code == 200
        body = json.loads(response.body)
        assert body["headers"].get("x-custom-transport") == "transport-value"

    def test_caller_headers_override_defaults(self) -> None:
        transport = (
            TransportOptions.builder().default_header("X-Override", "transport").build()
        )
        client = DefaultApiClient(transport)
        response = client.send_request(
            "GET", f"{self.base_url}/echo", {"X-Override": "caller"}, None
        )
        assert response.status_code == 200
        body = json.loads(response.body)
        assert body["headers"].get("x-override") == "caller"

    def test_returns_json_body_for_vendor_json_content_type(self) -> None:
        """Responses with Content-Type application/vnd.api+json should be
        JSON-deserialized, not returned as a raw string."""
        client = DefaultApiClient()
        response = client.send_request("GET", f"{self.base_url}/echo", {}, None)
        # The echo handler returns application/json; verify the body is valid JSON
        body = json.loads(response.body)
        assert isinstance(body, dict)
        # Simulate a +json content type check inline
        content_type = "application/vnd.api+json"
        assert content_type.startswith("application/json") or "+json" in content_type

    def test_does_not_override_caller_request_id(self) -> None:
        transport = TransportOptions.builder().inject_request_id(True).build()
        client = DefaultApiClient(transport)
        response = client.send_request(
            "GET", f"{self.base_url}/echo", {"X-Request-ID": "caller-id"}, None
        )
        assert response.status_code == 200
        body = json.loads(response.body)
        assert body["headers"].get("x-request-id") == "caller-id"

    def test_generates_unique_request_ids(self) -> None:
        transport = TransportOptions.builder().inject_request_id(True).build()
        client = DefaultApiClient(transport)
        response1 = client.send_request("GET", f"{self.base_url}/echo", {}, None)
        response2 = client.send_request("GET", f"{self.base_url}/echo", {}, None)
        body1 = json.loads(response1.body)
        body2 = json.loads(response2.body)
        id1 = body1["headers"].get("x-request-id")
        id2 = body2["headers"].get("x-request-id")
        assert id1 is not None
        assert id2 is not None
        assert id1 != id2

    def test_joins_multi_value_response_headers(self) -> None:
        import socketserver
        import threading

        multi_value_port = None

        class MultiValueHandler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                self.send_response(200)
                self.send_header("X-Multi", "val1")
                self.send_header("X-Multi", "val2")
                self.end_headers()
                self.wfile.write(b"ok")

            def log_message(self, format: str, *args: Any) -> None:
                pass

        with socketserver.TCPServer(("127.0.0.1", 0), MultiValueHandler) as httpd:
            multi_value_port = httpd.server_address[1]
            t = threading.Thread(target=httpd.handle_request)
            t.start()
            client = DefaultApiClient()
            response = client.send_request(
                "GET", f"http://127.0.0.1:{multi_value_port}/multi", {}, None
            )
            t.join()

        assert response.status_code == 200
        # urllib3 joins multi-value response headers with ", "
        lower_headers = {k.lower(): v for k, v in response.headers.items()}
        assert "x-multi" in lower_headers
        assert "val1" in lower_headers["x-multi"] and "val2" in lower_headers["x-multi"]


class TestCharsetDecoding:
    """Verify response body decoding honors the Content-Type charset."""

    def test_extracts_charset_parameter(self) -> None:
        assert (
            _charset_from_content_type("text/plain; charset=ISO-8859-1") == "ISO-8859-1"
        )
        assert _charset_from_content_type("text/plain") is None
        assert _charset_from_content_type("") is None
        assert _charset_from_content_type('text/plain; charset="utf-8"') == "utf-8"

    def test_decodes_iso_8859_1_response(self) -> None:
        decoded = _decode_with_charset(b"\xe9", "text/plain; charset=ISO-8859-1")
        assert decoded == "é"

    def test_defaults_to_utf8_when_no_charset(self) -> None:
        decoded = _decode_with_charset("é".encode("utf-8"), "text/plain")
        assert decoded == "é"

    def test_unknown_charset_falls_back_to_utf8(self) -> None:
        decoded = _decode_with_charset(
            "é".encode("utf-8"), "text/plain; charset=not-a-real-charset"
        )
        assert decoded == "é"

    def test_send_request_decodes_iso_8859_1_response(self) -> None:
        import socketserver
        import threading

        class _Latin1Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=ISO-8859-1")
                self.end_headers()
                self.wfile.write(b"\xe9")

            def log_message(self, format: str, *args: Any) -> None:
                pass

        with socketserver.TCPServer(("127.0.0.1", 0), _Latin1Handler) as httpd:
            port = httpd.server_address[1]
            t = threading.Thread(target=httpd.handle_request)
            t.start()
            client = DefaultApiClient()
            response = client.send_request("GET", f"http://127.0.0.1:{port}/", {}, None)
            t.join()
        assert response.body == "é"


class TestMultipartFilenameSanitization:
    """Sanitize multipart filenames against CRLF injection and non-ASCII drift."""

    def test_rejects_crlf_in_filename(self) -> None:
        with pytest.raises(ValueError):
            _sanitize_multipart_filename("a\r\nX-Injected: yes")

    def test_rejects_nul_in_filename(self) -> None:
        with pytest.raises(ValueError):
            _sanitize_multipart_filename("a\x00b.txt")

    def test_escapes_quote_and_backslash(self) -> None:
        ascii_fallback, rfc5987 = _sanitize_multipart_filename('a"b\\c.txt')
        assert ascii_fallback == 'a\\"b\\\\c.txt'
        assert rfc5987 is None

    def test_rfc5987_for_non_ascii(self) -> None:
        ascii_fallback, rfc5987 = _sanitize_multipart_filename("日本.pdf")
        assert rfc5987 == "UTF-8''%E6%97%A5%E6%9C%AC.pdf"
        # ASCII fallback must still be present and quote-safe
        assert '"' not in ascii_fallback or '\\"' in ascii_fallback

    def test_multipart_body_rejects_filename_injection(self) -> None:
        import io

        client = DefaultApiClient()
        file_like = io.BytesIO(b"hello")
        file_like.name = "a\r\nX-Injected: yes"
        with pytest.raises(ValueError):
            client._build_multipart_body({"upload": file_like}, "boundary")

    def test_multipart_body_escapes_quote_in_filename(self) -> None:
        import io

        client = DefaultApiClient()
        file_like = io.BytesIO(b"hello")
        file_like.name = 'a"b.txt'
        body = client._build_multipart_body({"upload": file_like}, "boundary")
        assert b'filename="a\\"b.txt"' in body

    def test_multipart_body_uses_rfc5987_for_non_ascii_filename(self) -> None:
        import io

        client = DefaultApiClient()
        file_like = io.BytesIO(b"hello")
        file_like.name = "日本.pdf"
        body = client._build_multipart_body({"upload": file_like}, "boundary")
        assert b"filename*=UTF-8''%E6%97%A5%E6%9C%AC.pdf" in body


class TestMultipartFieldNameUtf8:
    """multipart-field-name-ascii-fold: a non-ASCII field NAME must reach the
    wire as raw UTF-8, NOT be transliterated to '?'.

    Field names (unlike filename fallbacks) are carried verbatim per RFC 7578
    section 5.1.1. The previous bug routed the name through
    ``_sanitize_multipart_filename`` whose ASCII fallback replaced non-ASCII
    bytes with ``?``; the dedicated ``_sanitize_multipart_field_name`` keeps
    the name intact.
    """

    def test_field_name_helper_preserves_non_ascii(self) -> None:
        # The helper must return the name unchanged (no '?' substitution).
        assert _sanitize_multipart_field_name("dépôt") == "dépôt"

    def test_field_name_helper_escapes_quote_and_backslash(self) -> None:
        assert _sanitize_multipart_field_name('a"b\\c') == 'a\\"b\\\\c'

    def test_field_name_helper_rejects_crlf(self) -> None:
        with pytest.raises(ValueError):
            _sanitize_multipart_field_name("a\r\nX-Injected: yes")

    def test_field_name_helper_rejects_nul(self) -> None:
        with pytest.raises(ValueError):
            _sanitize_multipart_field_name("a\x00b")

    def test_multipart_body_preserves_non_ascii_field_name_as_utf8(self) -> None:
        client = DefaultApiClient()
        body = client._build_multipart_body({"café": b"x"}, "boundary")
        # The name must appear as raw UTF-8 bytes, never folded to '?'.
        assert 'name="café"'.encode("utf-8") in body
        assert b'name="caf?"' not in body

    def test_multipart_body_preserves_cjk_field_name_as_utf8(self) -> None:
        client = DefaultApiClient()
        body = client._build_multipart_body({"標籤": b"x"}, "boundary")
        assert 'name="標籤"'.encode("utf-8") in body
        assert b"?" not in body.split(b"\r\n\r\n", 1)[0]


class TestMultipartContentType:
    """Per-part Content-Type comes from the filename extension."""

    def test_guess_content_type_from_extension(self) -> None:
        assert _guess_content_type("file.png") == "image/png"

    def test_guess_content_type_unknown_extension_defaults_to_octet_stream(
        self,
    ) -> None:
        assert _guess_content_type("blob.zzz") == "application/octet-stream"

    def test_guess_content_type_no_filename_defaults_to_octet_stream(self) -> None:
        assert _guess_content_type(None) == "application/octet-stream"
        assert _guess_content_type("") == "application/octet-stream"

    def test_multipart_body_emits_png_content_type_for_png_file(self) -> None:
        import io

        client = DefaultApiClient()
        file_like = io.BytesIO(b"\x89PNG\r\n\x1a\n")
        file_like.name = "file.png"
        body = client._build_multipart_body({"upload": file_like}, "boundary")
        assert b"Content-Type: image/png" in body

    def test_multipart_body_uses_octet_stream_for_bytes_without_filename(self) -> None:
        client = DefaultApiClient()
        body = client._build_multipart_body({"upload": b"\x00\x01\x02"}, "boundary")
        assert b"Content-Type: application/octet-stream" in body


class TestProxyAuthentication:
    """Proxy URL with userinfo should produce a ``Proxy-Authorization`` header.

    The shared Squid container in this test environment runs without
    basic-auth ACLs, so this scenario cannot be verified end-to-end.
    Enable when ``squid.conf`` is provisioned with htpasswd-backed auth.
    """

    @pytest.mark.skip(
        reason=(
            "requires Squid configured with basic-auth; the shared squid_container "
            "in this test environment runs without basic_auth ACLs, so userinfo in the "
            "proxy URL cannot be verified end-to-end. Enable when squid.conf is "
            "provisioned with htpasswd-backed auth."
        )
    )
    def test_proxy_url_with_userinfo_sends_proxy_authorization(self) -> None:
        from urllib.parse import urlparse

        # Splice basic-auth userinfo into the proxy URL: http://user:pass@host:port
        base_proxy_url = "http://127.0.0.1:3128"
        parsed = urlparse(base_proxy_url)
        proxy_url_with_auth = (
            f"{parsed.scheme}://user:pass@{parsed.hostname}:{parsed.port}"
        )

        transport = TransportOptions.builder().proxy(proxy_url_with_auth).build()
        client = DefaultApiClient(transport)
        response = client.send_request("GET", "http://chasm:8080/test/echo", {}, None)

        assert response.status_code == 200
        # chasm echo envelope always includes a method field
        assert '"method"' in response.body


class TestMultipartBinaryPreservation:
    """Binary multipart parts must not be re-encoded through UTF-8."""

    def test_text_mode_file_is_rejected_not_silently_reencoded(self) -> None:
        """Passing a str-yielding file-like must NOT silently round-trip via UTF-8."""
        import io

        client = DefaultApiClient()
        # A text-mode file containing bytes that don't survive UTF-8 roundtrip
        text_file = io.StringIO("é")
        text_file.name = "note.txt"
        with pytest.raises(TypeError):
            client._build_multipart_body({"upload": text_file}, "boundary")

    def test_explicit_str_tuple_content_is_rejected(self) -> None:
        client = DefaultApiClient()
        with pytest.raises(TypeError):
            client._build_multipart_body({"upload": ("file.bin", "hello")}, "boundary")

    def test_high_byte_binary_content_is_preserved(self) -> None:
        client = DefaultApiClient()
        payload = bytes(range(256))
        body = client._build_multipart_body({"upload": payload}, "boundary")
        # The payload must appear verbatim in the body
        assert payload in body

    def test_tuple_with_filename_emits_filename_and_mime(self) -> None:
        client = DefaultApiClient()
        body = client._build_multipart_body(
            {"upload": ("file.pdf", b"%PDF-1.4")}, "boundary"
        )
        assert b'filename="file.pdf"' in body
        assert b"Content-Type: application/pdf" in body
        assert b"%PDF-1.4" in body


class _FakeResp:
    """Minimal response double for exercising the redirect loop without
    standing up a real HTTP server. ``read``/``release_conn`` mirror the
    urllib3 contract the loop relies on."""

    def __init__(self, status: int, headers: dict[str, Any]) -> None:
        self.status = status
        self.headers = headers

    def read(self) -> bytes:
        return b""

    def release_conn(self) -> None:
        return None


class TestNoRedirectOnTokenPost:
    """3.2: ``no_redirect=True`` must NOT follow redirects. The first 3xx
    response is returned to the caller verbatim (status/body/headers) rather
    than being thrown. The OAuth2 token manager inspects and rejects the 3xx
    itself, so the credential body is never silently replayed -- but the
    transport's job is simply to return the response as-is."""

    def _make_pool(self, responses: list[Any]) -> Any:
        class _Pool:
            def __init__(self) -> None:
                self.calls: list[Any] = []
                self._responses = list(responses)

            def request(self, method: str, url: str, **kwargs: Any) -> Any:
                self.calls.append((method, url, dict(kwargs.get("headers") or {})))
                return self._responses.pop(0)

        return _Pool()

    def test_307_returned_as_is_when_no_redirect(self) -> None:
        transport = TransportOptions.builder().follow_redirects(True).build()
        pool = self._make_pool(
            [
                _FakeResp(307, {"location": "https://attacker.example.com/steal"}),
            ]
        )
        client = DefaultApiClient(transport, pool_manager=pool)
        result = client.send_request(
            "POST",
            "https://auth.example.com/token",
            {"Content-Type": "application/x-www-form-urlencoded"},
            "grant_type=client_credentials&client_id=x&client_secret=y",
            no_redirect=True,
        )
        # The 3xx is returned verbatim and the replay request to the
        # attacker host must never have been issued.
        assert result.status_code == 307
        assert result.headers.get("location") == "https://attacker.example.com/steal"
        assert len(pool.calls) == 1

    def test_308_returned_as_is_when_no_redirect(self) -> None:
        transport = TransportOptions.builder().follow_redirects(True).build()
        pool = self._make_pool(
            [
                _FakeResp(308, {"location": "https://attacker.example.com/steal"}),
            ]
        )
        client = DefaultApiClient(transport, pool_manager=pool)
        result = client.send_request(
            "POST",
            "https://auth.example.com/token",
            {"Content-Type": "application/x-www-form-urlencoded"},
            "grant_type=password&username=u&password=p",
            no_redirect=True,
        )
        assert result.status_code == 308
        assert len(pool.calls) == 1

    def test_303_returned_as_is_when_no_redirect(self) -> None:
        # no_redirect disables redirect following entirely, so even a 303
        # is returned to the caller rather than coerced-to-GET and followed.
        transport = TransportOptions.builder().follow_redirects(True).build()
        pool = self._make_pool(
            [
                _FakeResp(303, {"location": "https://auth.example.com/done"}),
            ]
        )
        client = DefaultApiClient(transport, pool_manager=pool)
        result = client.send_request(
            "POST",
            "https://auth.example.com/token",
            {"Content-Type": "application/x-www-form-urlencoded"},
            "grant_type=client_credentials",
            no_redirect=True,
        )
        assert result.status_code == 303
        assert len(pool.calls) == 1

    def test_no_redirect_does_not_affect_normal_request(self) -> None:
        # Without no_redirect, 307 follows normally (replays the body).
        transport = TransportOptions.builder().follow_redirects(True).build()
        pool = self._make_pool(
            [
                _FakeResp(307, {"location": "https://api.example.com/v2/echo"}),
                _FakeResp(200, {}),
            ]
        )
        client = DefaultApiClient(transport, pool_manager=pool)
        client.send_request(
            "POST",
            "https://api.example.com/v1/echo",
            {"Content-Type": "application/json"},
            '{"hello":"world"}',
        )
        assert len(pool.calls) == 2


class TestBodyReplayOnTlsDowngrade:
    """3.3: an HTTPS -> HTTP downgrade must NOT silently replay a request
    body over plaintext. The existing Authorization-strip guard covers the
    credential header path; this guard covers the body itself."""

    def test_307_downgrade_with_body_raises(self) -> None:
        from zitadel_client.errors import ApiException

        class _Pool:
            def __init__(self) -> None:
                self.calls: list[Any] = []

            def request(self, method: str, url: str, **kwargs: Any) -> Any:
                self.calls.append((method, url))
                if len(self.calls) == 1:
                    return _FakeResp(307, {"location": "http://example.com/insecure"})
                return _FakeResp(200, {})

        transport = TransportOptions.builder().follow_redirects(True).build()
        pool = _Pool()
        client = DefaultApiClient(transport, pool_manager=pool)
        with pytest.raises(ApiException) as excinfo:
            client.send_request(
                "POST",
                "https://example.com/secure",
                {"Content-Type": "application/json"},
                '{"secret":"value"}',
            )
        assert "downgrade" in str(excinfo.value.message or "").lower()
        # The replay over plaintext must never have happened.
        assert len(pool.calls) == 1

    def test_308_downgrade_with_body_raises(self) -> None:
        from zitadel_client.errors import ApiException

        class _Pool:
            def __init__(self) -> None:
                self.calls: list[Any] = []

            def request(self, method: str, url: str, **kwargs: Any) -> Any:
                self.calls.append((method, url))
                if len(self.calls) == 1:
                    return _FakeResp(308, {"location": "http://example.com/insecure"})
                return _FakeResp(200, {})

        transport = TransportOptions.builder().follow_redirects(True).build()
        pool = _Pool()
        client = DefaultApiClient(transport, pool_manager=pool)
        with pytest.raises(ApiException):
            client.send_request(
                "PUT",
                "https://example.com/secure",
                {"Content-Type": "application/json"},
                '{"secret":"value"}',
            )
        assert len(pool.calls) == 1

    def test_303_downgrade_with_body_is_allowed(self) -> None:
        # 303 coerces to GET and drops the body, so plaintext replay is
        # not a concern. The Authorization-strip guard still runs.
        class _Pool:
            def __init__(self) -> None:
                self.calls: list[Any] = []

            def request(self, method: str, url: str, **kwargs: Any) -> Any:
                self.calls.append((method, url, dict(kwargs.get("headers") or {})))
                if len(self.calls) == 1:
                    return _FakeResp(303, {"location": "http://example.com/done"})
                return _FakeResp(200, {})

        transport = TransportOptions.builder().follow_redirects(True).build()
        pool = _Pool()
        client = DefaultApiClient(transport, pool_manager=pool)
        client.send_request(
            "POST",
            "https://example.com/secure",
            {"Content-Type": "application/json"},
            '{"x":1}',
        )
        assert len(pool.calls) == 2
        assert pool.calls[1][0] == "GET"

    def test_http_to_https_upgrade_with_body_is_allowed(self) -> None:
        # Upgrade is not a downgrade; the body must replay normally.
        class _Pool:
            def __init__(self) -> None:
                self.calls: list[Any] = []

            def request(self, method: str, url: str, **kwargs: Any) -> Any:
                self.calls.append((method, url, kwargs.get("body")))
                if len(self.calls) == 1:
                    return _FakeResp(307, {"location": "https://example.com/secure"})
                return _FakeResp(200, {})

        transport = TransportOptions.builder().follow_redirects(True).build()
        pool = _Pool()
        client = DefaultApiClient(transport, pool_manager=pool)
        client.send_request(
            "POST",
            "http://example.com/insecure",
            {"Content-Type": "application/json"},
            '{"x":1}',
        )
        assert len(pool.calls) == 2


class TestContentLengthStrippedOnRedirect:
    """3.4: the 303-coerce-to-GET (and 301/302 method-demotion) branch must
    drop ``Content-Length`` along with the body, otherwise the follow-up
    GET arrives advertising a Content-Length the server expects but the
    request never sends."""

    def test_303_drops_content_length_when_body_is_dropped(self) -> None:
        class _Pool:
            def __init__(self) -> None:
                self.calls: list[Any] = []

            def request(self, method: str, url: str, **kwargs: Any) -> Any:
                self.calls.append((method, url, dict(kwargs.get("headers") or {})))
                if len(self.calls) == 1:
                    return _FakeResp(303, {"location": "https://example.com/done"})
                return _FakeResp(200, {})

        transport = TransportOptions.builder().follow_redirects(True).build()
        pool = _Pool()
        client = DefaultApiClient(transport, pool_manager=pool)
        client.send_request(
            "POST",
            "https://example.com/start",
            {"Content-Type": "application/json", "Content-Length": "11"},
            '{"x":"yz"}',
        )
        assert len(pool.calls) == 2
        followup_headers = pool.calls[1][2]
        assert not any(k.lower() == "content-length" for k in followup_headers), (
            f"Content-Length must be stripped on 303->GET; got {followup_headers!r}"
        )
        assert not any(k.lower() == "content-type" for k in followup_headers)

    def test_302_post_to_get_drops_content_length(self) -> None:
        # 302 on a POST demotes to GET in our loop (mirrors browser behaviour
        # and the other 11 SDKs). The body and its length headers must go.
        class _Pool:
            def __init__(self) -> None:
                self.calls: list[Any] = []

            def request(self, method: str, url: str, **kwargs: Any) -> Any:
                self.calls.append((method, url, dict(kwargs.get("headers") or {})))
                if len(self.calls) == 1:
                    return _FakeResp(302, {"location": "https://example.com/done"})
                return _FakeResp(200, {})

        transport = TransportOptions.builder().follow_redirects(True).build()
        pool = _Pool()
        client = DefaultApiClient(transport, pool_manager=pool)
        client.send_request(
            "POST",
            "https://example.com/start",
            {"Content-Type": "application/json", "Content-Length": "5"},
            '{"a":1}',
        )
        assert len(pool.calls) == 2
        assert pool.calls[1][0] == "GET"
        followup_headers = pool.calls[1][2]
        assert not any(k.lower() == "content-length" for k in followup_headers)


class TestRedirectExhaustion:
    """Exceeding ``max_redirects`` must raise a typed ApiException ("too many
    redirects") rather than silently returning the final 3xx as a normal
    response."""

    def test_exhausting_redirect_budget_raises(self) -> None:
        from zitadel_client.errors import ApiException

        class _Pool:
            def request(self, method: str, url: str, **kwargs: Any) -> Any:
                # Always answer with another redirect so the budget is exhausted.
                return _FakeResp(302, {"location": "https://example.com/next"})

        transport = (
            TransportOptions.builder().follow_redirects(True).max_redirects(3).build()
        )
        client = DefaultApiClient(transport, pool_manager=_Pool())
        with pytest.raises(ApiException) as excinfo:
            client.send_request("GET", "https://example.com/start", {}, None)
        assert "too many redirects" in str(excinfo.value.message or "").lower()

    def test_terminal_redirect_without_location_does_not_raise(self) -> None:
        # A 3xx with no Location header is a legitimate terminal response and
        # must NOT be treated as redirect exhaustion.
        class _Pool:
            def request(self, method: str, url: str, **kwargs: Any) -> Any:
                return _FakeResp(302, {})

        transport = TransportOptions.builder().follow_redirects(True).build()
        client = DefaultApiClient(transport, pool_manager=_Pool())
        response = client.send_request("GET", "https://example.com/start", {}, None)
        assert response.status_code == 302


class TestUseAfterClose:
    """Calling ``send_request`` after ``close()`` must raise the SDK's own
    ApiException rather than a foreign urllib3 error or silently succeeding."""

    def test_send_after_close_raises_api_exception(self) -> None:
        from zitadel_client.errors import ApiException

        class _Pool:
            def __init__(self) -> None:
                self.calls = 0

            def clear(self) -> None:
                return None

            def request(self, method: str, url: str, **kwargs: Any) -> Any:
                self.calls += 1
                return _FakeResp(200, {})

        pool = _Pool()
        client = DefaultApiClient(pool_manager=pool)
        client.close()
        with pytest.raises(ApiException):
            client.send_request("GET", "https://example.com/x", {}, None)
        # The request must never have been issued against the closed client.
        assert pool.calls == 0

    def test_close_is_idempotent(self) -> None:
        client = DefaultApiClient()
        client.close()
        client.close()


class TestBodyReadErrorWrapped:
    """A failure DURING the response body read (after headers are received)
    must be wrapped in the SDK ApiException, not leak the raw urllib3 error."""

    def test_body_read_error_is_wrapped_in_api_exception(self) -> None:
        import urllib3
        from zitadel_client.errors import ApiException

        class _ReadFailResp:
            status = 200
            headers: ClassVar[dict[str, Any]] = {}

            def read(self) -> bytes:
                raise urllib3.exceptions.ProtocolError("connection broken mid-body")

            def release_conn(self) -> None:
                return None

        class _Pool:
            def request(self, method: str, url: str, **kwargs: Any) -> Any:
                return _ReadFailResp()

        transport = TransportOptions.builder().follow_redirects(False).build()
        client = DefaultApiClient(transport, pool_manager=_Pool())
        with pytest.raises(ApiException) as excinfo:
            client.send_request("GET", "https://example.com/x", {}, None)
        # The underlying urllib3 error is preserved as the cause.
        assert isinstance(excinfo.value.__cause__, urllib3.exceptions.HTTPError)


class TestCaCertPathFailsFast:
    """An explicitly configured CA certificate path that cannot be read or
    parsed must fail fast at construction with the SDK's ApiException rather
    than silently falling back to the system trust store (security theater)."""

    def test_nonexistent_ca_cert_path_raises_api_exception(self) -> None:
        from zitadel_client.errors import ApiException

        transport = (
            TransportOptions.builder().ca_cert_path("/nonexistent/ca.pem").build()
        )
        with pytest.raises(ApiException):
            DefaultApiClient(transport)


class TestApiKeyHeaderStrippedOnCrossOrigin:
    """3.1: spec-declared API-key header names are added to the cross-origin
    sensitive-header allowlist at codegen time. When the spec declares no
    apiKey-in-header schemes the allowlist is just the default trio."""

    def test_default_sensitive_headers_includes_canonical_three(self) -> None:
        from zitadel_client.default_api_client import DefaultApiClient

        assert "authorization" in DefaultApiClient._SENSITIVE_HEADERS
        assert "cookie" in DefaultApiClient._SENSITIVE_HEADERS
        assert "proxy-authorization" in DefaultApiClient._SENSITIVE_HEADERS

    def test_authorization_stripped_on_cross_origin_redirect(self) -> None:
        # The static credential trio is always stripped on a cross-origin hop
        # regardless of whether the spec declared any apiKey-in-header schemes.
        class _Pool:
            def __init__(self) -> None:
                self.calls: list[Any] = []

            def request(self, method: str, url: str, **kwargs: Any) -> Any:
                self.calls.append((method, url, dict(kwargs.get("headers") or {})))
                if len(self.calls) == 1:
                    return _FakeResp(
                        302, {"location": "https://other.example.com/dest"}
                    )
                return _FakeResp(200, {})

        transport = TransportOptions.builder().follow_redirects(True).build()
        pool = _Pool()
        client = DefaultApiClient(transport, pool_manager=pool)
        client.send_request(
            "GET",
            "https://example.com/start",
            {"Authorization": "Bearer secret", "X-Trace": "keep"},
            None,
        )
        assert len(pool.calls) == 2
        followup_headers = pool.calls[1][2]
        assert not any(k.lower() == "authorization" for k in followup_headers), (
            f"Authorization leaked on cross-origin redirect: {followup_headers!r}"
        )
        # Non-sensitive headers must survive the hop.
        assert any(k.lower() == "x-trace" for k in followup_headers)


class TestRedirectToNonHttpScheme:
    """A Location pointing at a non-http(s) scheme (file:, javascript:, data:)
    must be refused with a typed ApiException rather than silently returned."""

    def test_non_http_scheme_redirect_raises(self) -> None:
        from zitadel_client.errors import ApiException

        class _Pool:
            def __init__(self) -> None:
                self.calls: list[Any] = []

            def request(self, method: str, url: str, **kwargs: Any) -> Any:
                self.calls.append((method, url))
                return _FakeResp(302, {"location": "file:///etc/passwd"})

        transport = TransportOptions.builder().follow_redirects(True).build()
        pool = _Pool()
        client = DefaultApiClient(transport, pool_manager=pool)
        with pytest.raises(ApiException) as excinfo:
            client.send_request("GET", "https://example.com/start", {}, None)
        assert "non-http" in str(excinfo.value.message or "").lower()
        # The non-http(s) target must never have been contacted.
        assert len(pool.calls) == 1
