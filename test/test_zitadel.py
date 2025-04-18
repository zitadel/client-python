import importlib
import inspect
import pkgutil
import unittest

from zitadel_client.auth.no_auth_authenticator import NoAuthAuthenticator
from zitadel_client.zitadel import Zitadel


class ZitadelServicesTest(unittest.TestCase):
    """
    Test to verify that all API service classes defined in the "zitadel_client.api" namespace
    are registered as attributes in the Zitadel class.
    """

    def test_services_dynamic(self) -> None:
        expected = set()
        package = importlib.import_module("zitadel_client.api")
        for _, modname, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            module = importlib.import_module(modname)
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ == modname and obj.__name__.endswith("ServiceApi"):
                    expected.add(obj)
        zitadel = Zitadel(NoAuthAuthenticator("http://dummy"))
        actual = {
            type(getattr(zitadel, attr))
            for attr in dir(zitadel)
            if not attr.startswith("_")
            and hasattr(getattr(zitadel, attr), "__class__")
            and getattr(zitadel, attr).__class__.__module__.startswith("zitadel_client.api")
        }
        self.assertEqual(expected, actual)
