import unittest

from zitadel_client.exceptions import ApiError


class ApiExceptionTest(unittest.TestCase):
    def test_api_exception(self) -> None:
        headers = {"H": "v"}
        e = ApiError(418, headers, "body")

        self.assertEqual(str(e), "Error 418")
        self.assertEqual(e.code, 418)
        self.assertEqual(e.response_headers, headers)
        self.assertEqual(e.response_body, "body")
