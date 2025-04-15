import os
import tempfile
import uuid

import pytest

import zitadel_client as zitadel
from zitadel_client.auth.web_token_authenticator import WebTokenAuthenticator


@pytest.fixture
def key_file():
    jwt_key = os.getenv("JWT_KEY")
    if jwt_key is None:
        pytest.fail("JWT_KEY is not set in the environment")
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as tf:
        tf.write(jwt_key)
        return tf.name


@pytest.fixture
def base_url():
    """Fixture to return the base URL."""
    return os.getenv("BASE_URL")


@pytest.fixture
def user_id(key_file, base_url):
    """Fixture to create a user and return their ID."""
    with zitadel.Zitadel(WebTokenAuthenticator.from_json(base_url, key_file)) as client:
        try:
            response = client.users.add_human_user(
                body=zitadel.models.V2AddHumanUserRequest(
                    username=uuid.uuid4().hex,
                    profile=zitadel.models.V2SetHumanProfile(given_name="John", family_name="Doe"),
                    email=zitadel.models.V2SetHumanEmail(email=f"johndoe{uuid.uuid4().hex}@caos.ag")
                )
            )
            print("User created:", response)
            return response.user_id
        except Exception as e:
            pytest.fail(f"Exception while creating user: {e}")


def test_should_deactivate_and_reactivate_user_with_valid_token(user_id, key_file, base_url):
    """Test to (de)activate the user with a valid token."""
    with zitadel.Zitadel(WebTokenAuthenticator.from_json(base_url, key_file)) as client:
        try:
            deactivate_response = client.users.deactivate_user(user_id=user_id)
            print("User deactivated:", deactivate_response)

            reactivate_response = client.users.reactivate_user(user_id=user_id)
            print("User reactivated:", reactivate_response)
            # Adjust based on actual response format
            # assert reactivate_response["status"] == "success"
        except Exception as e:
            pytest.fail(f"Exception when calling deactivate_user or reactivate_user with valid token: {e}")
