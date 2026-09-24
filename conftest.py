import importlib.util
import os
import time

import pytest

# Every dependency an emitted test imports is listed, with the test that needs
# it, in .openapi-generator/DEV-DEPENDENCIES. A client keep-lists its own
# pyproject.toml, so a dependency the generator started using is missing there
# until someone copies it across -- and the whole suite then dies at collection
# with an ImportError from whichever module happened to be imported first.
# Probing here turns that into one message that names the file to reconcile
# against. The distributions below are imported inside the fixtures rather than
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
def chasm_container(proxy_network):
    from testcontainers.core.container import DockerContainer
    from testcontainers.core.wait_strategies import LogMessageWaitStrategy

    host_app_path = os.environ.get("HOST_APP_PATH", os.getcwd())
    spec_path = os.path.join(host_app_path, "test", "fixtures", "openapi.yaml")
    cert_path = os.path.join(host_app_path, "test", "fixtures", "certs", "server.pem")
    key_path = os.path.join(
        host_app_path, "test", "fixtures", "certs", "server-key.pem"
    )

    container = (
        DockerContainer("mridang/chasm:1.3.0")
        .with_exposed_ports(4010, 8443)
        .with_volume_mapping(spec_path, "/tmp/openapi.yaml", "ro")
        .with_volume_mapping(cert_path, "/certs/cert.pem", "ro")
        .with_volume_mapping(key_path, "/certs/key.pem", "ro")
        .with_command(
            "mock /tmp/openapi.yaml --host 0.0.0.0 "
            "--tls-cert /certs/cert.pem --tls-key /certs/key.pem --tls-port 8443"
        )
        .waiting_for(LogMessageWaitStrategy("Listening on"))
    )
    container.start()
    proxy_network.connect(container.get_wrapped_container().id, aliases=["chasm"])
    yield container
    container.stop()


@pytest.fixture(scope="session")
def api_base_url(chasm_container):
    host = chasm_container.get_container_host_ip()
    port = chasm_container.get_exposed_port(4010)
    return f"http://{host}:{port}"


@pytest.fixture(scope="session")
def chasm_http_url(chasm_container):
    host = chasm_container.get_container_host_ip()
    port = chasm_container.get_exposed_port(4010)
    return f"http://{host}:{port}"


@pytest.fixture(scope="session")
def chasm_https_url(chasm_container):
    host = chasm_container.get_container_host_ip()
    port = chasm_container.get_exposed_port(8443)
    return f"https://{host}:{port}"


@pytest.fixture(scope="session")
def chasm_internal_http_url():
    return "http://chasm:4010"


@pytest.fixture(scope="session")
def chasm_internal_https_url():
    return "https://chasm:8443"


@pytest.fixture(scope="session")
def proxy_network():
    import docker

    client = docker.from_env()
    network = client.networks.create("proxy-test-network")
    yield network
    network.remove()


@pytest.fixture(scope="session")
def squid_container(proxy_network):
    from testcontainers.core.container import DockerContainer

    host_app_path = os.environ.get("HOST_APP_PATH", os.getcwd())
    squid_conf_path = os.path.join(
        host_app_path, "test", "fixtures", "proxy", "squid.conf"
    )

    # ubuntu/squid declares VOLUME /var/log/squid and VOLUME /var/spool/squid,
    # so every proxy container Docker creates leaves two anonymous volumes
    # behind after the suite stops it. Mounting both as tmpfs keeps the
    # container writable without allocating a volume. mode=1777 because squid
    # drops to the unprivileged `proxy` user before it opens its logs.
    container = (
        DockerContainer("ubuntu/squid:5.2-22.04_beta")
        .with_exposed_ports(3128, 3129)
        .with_volume_mapping(squid_conf_path, "/etc/squid/squid.conf", "ro")
        .with_tmpfs_mount("/var/log/squid", "rw,mode=1777")
        .with_tmpfs_mount("/var/spool/squid", "rw,mode=1777")
    )
    container.start()
    proxy_network.connect(container.get_wrapped_container().id)
    time.sleep(3)
    yield container
    container.stop()


@pytest.fixture(scope="session")
def proxy_url(squid_container):
    host = squid_container.get_container_host_ip()
    port = squid_container.get_exposed_port(3128)
    return f"http://{host}:{port}"


@pytest.fixture(scope="session")
def proxy_auth_host_port(squid_container):
    """host:port of the fixture proxy port that requires Basic credentials."""
    host = squid_container.get_container_host_ip()
    port = squid_container.get_exposed_port(3129)
    return f"{host}:{port}"


@pytest.fixture(scope="session")
def ca_cert_path():
    return os.path.join(os.getcwd(), "test", "fixtures", "certs", "ca.pem")
