import logging
import os
import shlex
import subprocess
import time
from typing import Dict, Generator

import pytest

LOGGER = logging.getLogger(__name__)
COMPOSE_FILE_PATH: str = os.path.join(os.path.dirname(__file__), "..", "etc", "docker-compose.yaml")
COMPOSE_FILE_DIR: str = os.path.dirname(COMPOSE_FILE_PATH)


@pytest.fixture(scope="module")
def docker_compose() -> Generator[Dict[str, str], None, None]:
    """
    Abstract base class for integration tests that interact with a Docker
    Compose stack.

    This fixture handles the lifecycle of the Docker Compose environment,
    bringing it up before tests run and tearing it down afterwards. It also
    provides mechanisms to load specific data (like authentication tokens
    and JWT keys) from files and makes them accessible via the returned dictionary.

    Yields:
        dict: A dictionary containing:
            - "auth_token" (str): The authentication token loaded from a file.
            - "jwt_key" (str): The absolute path to the JWT key file.
            - "base_url" (str): The base URL for the services.

    After the tests are finished, the Docker Compose stack is torn down.
    """
    LOGGER.info("Bringing up Docker Compose stack...")
    command: list[str] = [
        "docker",
        "compose",
        "--file",
        shlex.quote(COMPOSE_FILE_PATH),
        "up",
        "--detach",
        "--no-color",
        "--quiet-pull",
        "--yes",
    ]
    result = subprocess.run(command, capture_output=True, text=True)  # noqa: S603

    LOGGER.info(result.stdout)
    if result.returncode != 0:
        error_message: str = f"Failed to bring up Docker Compose stack. Exit code: {result.returncode}\n{result.stderr}"
        raise RuntimeError(error_message)
    LOGGER.info("Docker Compose stack is up.")

    auth_token_path: str = os.path.join(COMPOSE_FILE_DIR, "zitadel_output", "pat.txt")
    if os.path.exists(auth_token_path):
        with open(auth_token_path, "r") as f:
            auth_token = f.read().strip()
        LOGGER.info(f"Loaded authToken: {auth_token}")
    else:
        raise Exception(f"Auth token file not found at: {auth_token_path}")

    jwt_key_path: str = os.path.join(COMPOSE_FILE_DIR, "zitadel_output", "sa-key.json")
    if not os.path.exists(jwt_key_path):
        raise Exception(f"JWT Key file not found at path: {jwt_key_path}")
    jwt_key = jwt_key_path
    LOGGER.info(f"Loaded JWT_KEY path: {jwt_key}")

    base_url: str = "http://localhost:8099"
    LOGGER.info(f"Exposed BASE_URL: {base_url}")

    time.sleep(20)

    yield {
        "auth_token": auth_token,
        "jwt_key": jwt_key,
        "base_url": base_url,
    }

    LOGGER.info("Tearing down Docker Compose stack...")
    command = ["docker", "compose", "--file", shlex.quote(COMPOSE_FILE_PATH), "down", "-v"]
    result = subprocess.run(command, capture_output=True, text=True)  # noqa: S603

    LOGGER.info(result.stdout)
    if result.returncode != 0:
        LOGGER.warning(f"Failed to tear down Docker Compose stack. Exit code: {result.returncode}\n{result.stderr}")
    else:
        LOGGER.info("Docker Compose stack torn down.")
