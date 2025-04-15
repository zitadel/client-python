import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load the .env file for the entire test session."""
    load_dotenv()
