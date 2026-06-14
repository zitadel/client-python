# ruff: noqa
# mypy: ignore-errors
import os
import time

import docker
import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy


@pytest.fixture(scope="session")
def chasm_container(proxy_network):
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
    proxy_network.connect(container._container.id, aliases=["chasm"])
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
    client = docker.from_env()
    network = client.networks.create("proxy-test-network")
    yield network
    network.remove()


@pytest.fixture(scope="session")
def squid_container(proxy_network):
    host_app_path = os.environ.get("HOST_APP_PATH", os.getcwd())
    squid_conf_path = os.path.join(
        host_app_path, "test", "fixtures", "proxy", "squid.conf"
    )

    container = (
        DockerContainer("ubuntu/squid:5.2-22.04_beta")
        .with_exposed_ports(3128)
        .with_volume_mapping(squid_conf_path, "/etc/squid/squid.conf", "ro")
    )
    container.start()
    proxy_network.connect(container._container.id)
    time.sleep(3)
    yield container
    container.stop()


@pytest.fixture(scope="session")
def proxy_url(squid_container):
    host = squid_container.get_container_host_ip()
    port = squid_container.get_exposed_port(3128)
    return f"http://{host}:{port}"


@pytest.fixture(scope="session")
def ca_cert_path():
    return os.path.join(os.getcwd(), "test", "fixtures", "certs", "ca.pem")
