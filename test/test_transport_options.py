import unittest

from zitadel_client.transport_options import TransportOptions


class TransportOptionsTest(unittest.TestCase):

    def test_defaults_returns_empty(self) -> None:
        self.assertEqual({}, TransportOptions.defaults().to_session_kwargs())

    def test_insecure_sets_verify_false(self) -> None:
        opts = TransportOptions(insecure=True)
        self.assertEqual({"verify": False}, opts.to_session_kwargs())

    def test_ca_cert_path_sets_verify(self) -> None:
        opts = TransportOptions(ca_cert_path="/path/to/ca.pem")
        self.assertEqual({"verify": "/path/to/ca.pem"}, opts.to_session_kwargs())

    def test_proxy_url_sets_proxies(self) -> None:
        opts = TransportOptions(proxy_url="http://proxy:3128")
        self.assertEqual(
            {"proxies": {"http": "http://proxy:3128", "https": "http://proxy:3128"}},
            opts.to_session_kwargs(),
        )

    def test_insecure_takes_precedence_over_ca_cert(self) -> None:
        opts = TransportOptions(insecure=True, ca_cert_path="/path/to/ca.pem")
        self.assertEqual({"verify": False}, opts.to_session_kwargs())

    def test_immutability(self) -> None:
        opts = TransportOptions.defaults()
        with self.assertRaises(AttributeError):
            opts.insecure = True  # type: ignore[misc]

    def test_defaults_factory(self) -> None:
        opts = TransportOptions.defaults()
        self.assertEqual({}, dict(opts.default_headers))
        self.assertIsNone(opts.ca_cert_path)
        self.assertFalse(opts.insecure)
        self.assertIsNone(opts.proxy_url)
