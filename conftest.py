import importlib.util
import os

import pytest

# Every dependency an emitted test imports is listed, with the test that needs
# it, in .openapi-generator/DEV-DEPENDENCIES. A client keep-lists its own
# pyproject.toml, so a dependency the generator started using is missing there
# until someone copies it across -- and the whole suite then dies at collection
# with an ImportError from whichever module happened to be imported first.
# Probing here turns that into one message that names the file to reconcile
# against. The distributions below are imported inside the tests rather than
# at module scope so this check runs before the failure it is reporting on.
DEV_DEPENDENCIES = ".openapi-generator/DEV-DEPENDENCIES"

_REQUIRED_TEST_DISTRIBUTIONS = {
    "docker": "docker",
    "opentelemetry.sdk.trace": "opentelemetry-sdk",
    "pytest_asyncio": "pytest-asyncio",
    "pytest_cov": "pytest-cov",
    "testcontainers": "testcontainers",
}


def _is_installed(module):
    # find_spec imports the parent package of a dotted name, so it raises
    # rather than returning None when the parent is the part that is missing.
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, ValueError):
        return False


def _assert_test_dependencies_installed():
    missing = sorted(
        distribution
        for module, distribution in _REQUIRED_TEST_DISTRIBUTIONS.items()
        if not _is_installed(module)
    )
    if missing:
        raise RuntimeError(
            "Missing test dependencies: "
            + ", ".join(missing)
            + ". Every dependency the generated tests import is listed in "
            + DEV_DEPENDENCIES
            + "; add the missing entries to this project's dependency manifest "
            "and reinstall."
        )


_assert_test_dependencies_installed()


@pytest.fixture(scope="session")
def ca_cert_path():
    return os.path.join(os.getcwd(), "test", "fixtures", "certs", "ca.pem")
