from zitadel_client.api.feature_service_api import FeatureServiceApi
from zitadel_client.api.identity_provider_service_api import IdentityProviderServiceApi
from zitadel_client.api.oidc_service_api import OIDCServiceApi
from zitadel_client.api.organization_service_api import OrganizationServiceApi
from zitadel_client.api.session_service_api import SessionServiceApi
from zitadel_client.api.settings_service_api import SettingsServiceApi
from zitadel_client.api.user_service_api import UserServiceApi
from zitadel_client.api_client import ApiClient
from zitadel_client.auth.authenticator import Authenticator
from zitadel_client.configuration import Configuration


class Zitadel:
    """
    Main entry point for the Zitadel SDK.

    This class initializes and configures the SDK with the provided authentication strategy.
    It sets up service APIs for interacting with various Zitadel features such as identity providers,
    organizations, sessions, settings, users, and more.

    Attributes:
        configuration (Configuration): The configuration instance containing authentication and endpoint details.
        client (ApiClient): The API client used for making HTTP requests to the Zitadel API.
        features (FeatureServiceApi): Service API for feature management.
        idps (IdentityProviderServiceApi): Service API for identity provider operations.
        oidc (OIDCServiceApi): Service API for OIDC-related operations.
        organizations (OrganizationServiceApi): Service API for organization-related operations.
        sessions (SessionServiceApi): Service API for session management.
        settings (SettingsServiceApi): Service API for settings management.
        users (UserServiceApi): Service API for user management.
    """

    def __init__(self, authenticator: Authenticator, mutate_config: callable = None):
        """
        Initialize the Zitadel SDK.

        This constructor creates a configuration instance using the provided authenticator.
        Optionally, the configuration can be modified via the `mutate_config` callback function.
        It then instantiates the underlying API client and initializes various service APIs.

        Args:
            authenticator (Authenticator): The authentication strategy to be used.
            mutate_config (callable, optional): A callback function that receives the configuration
                instance for any additional modifications before the API client is created.
                Defaults to None.
        """
        self.configuration = Configuration(authenticator)

        if mutate_config:
            mutate_config(self.configuration)

        client = ApiClient(configuration=self.configuration)
        self.features = FeatureServiceApi(client)
        self.idps = IdentityProviderServiceApi(client)
        self.oidc = OIDCServiceApi(client)
        self.organizations = OrganizationServiceApi(client)
        self.sessions = SessionServiceApi(client)
        self.settings = SettingsServiceApi(client)
        self.users = UserServiceApi(client)

    def __enter__(self):
        """
        Enter the runtime context related to the Zitadel instance.

        Returns:
            Zitadel: The current instance.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the runtime context.

        This method can be used to perform cleanup actions. Currently, it does nothing.

        Args:
            exc_type: The exception type, if an exception occurred.
            exc_value: The exception value, if an exception occurred.
            traceback: The traceback of the exception, if an exception occurred.
        """
        pass
