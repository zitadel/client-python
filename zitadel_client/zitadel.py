from types import TracebackType
from typing import Callable, Optional, Type, TypeVar

from zitadel_client.api.beta_action_service_api import BetaActionServiceApi
from zitadel_client.api.beta_app_service_api import BetaAppServiceApi
from zitadel_client.api.beta_authorization_service_api import BetaAuthorizationServiceApi
from zitadel_client.api.beta_feature_service_api import BetaFeatureServiceApi
from zitadel_client.api.beta_instance_service_api import BetaInstanceServiceApi
from zitadel_client.api.beta_internal_permission_service_api import BetaInternalPermissionServiceApi
from zitadel_client.api.beta_oidc_service_api import BetaOIDCServiceApi
from zitadel_client.api.beta_organization_service_api import BetaOrganizationServiceApi
from zitadel_client.api.beta_project_service_api import BetaProjectServiceApi
from zitadel_client.api.beta_session_service_api import BetaSessionServiceApi
from zitadel_client.api.beta_settings_service_api import BetaSettingsServiceApi
from zitadel_client.api.beta_telemetry_service_api import BetaTelemetryServiceApi
from zitadel_client.api.beta_user_service_api import BetaUserServiceApi
from zitadel_client.api.beta_web_key_service_api import BetaWebKeyServiceApi
from zitadel_client.api.feature_service_api import FeatureServiceApi
from zitadel_client.api.identity_provider_service_api import IdentityProviderServiceApi
from zitadel_client.api.oidc_service_api import OIDCServiceApi
from zitadel_client.api.organization_service_api import OrganizationServiceApi
from zitadel_client.api.saml_service_api import SAMLServiceApi
from zitadel_client.api.session_service_api import SessionServiceApi
from zitadel_client.api.settings_service_api import SettingsServiceApi
from zitadel_client.api.user_service_api import UserServiceApi
from zitadel_client.api.web_key_service_api import WebKeyServiceApi
from zitadel_client.api_client import ApiClient
from zitadel_client.auth.authenticator import Authenticator
from zitadel_client.auth.client_credentials_authenticator import ClientCredentialsAuthenticator
from zitadel_client.auth.personal_access_token_authenticator import PersonalAccessTokenAuthenticator
from zitadel_client.auth.web_token_authenticator import WebTokenAuthenticator
from zitadel_client.configuration import Configuration


class Zitadel:
    """
    Main entry point for the Zitadel SDK.

    This class initializes and configures the SDK with the provided authentication strategy.
    It sets up service APIs for interacting with various Zitadel features such as identity providers,
    organizations, sessions, settings, users, and more.

    Attributes:
    features (FeatureServiceApi)
        Endpoints for feature management.
    idps (IdentityProviderServiceApi)
        Endpoints for identity-provider operations.
    oidc (OIDCServiceApi)
        Endpoints for OIDC-related operations.
    organizations (OrganizationServiceApi)
        Endpoints for organization management.
    saml (SAMLServiceApi)
        Endpoints for SAML identity-provider management.
    sessions (SessionServiceApi)
        Endpoints for session lifecycle management.
    settings (SettingsServiceApi)
        Endpoints for organization- and instance-level settings.
    users (UserServiceApi)
        Endpoints for end-user management.
    webkeys (WebKeyServiceApi)
        Endpoints for WebCrypto keys (JWKS).
    beta_projects (BetaProjectServiceApi)
        Preview endpoints for project management.
    beta_apps (BetaAppServiceApi)
        Preview endpoints for application registration.
    beta_oidc (BetaOIDCServiceApi)
        Preview endpoints for OIDC features not yet GA.
    beta_users (BetaUserServiceApi)
        Preview endpoints for advanced user management.
    beta_organizations (BetaOrganizationServiceApi)
        Preview endpoints for organization features.
    beta_settings (BetaSettingsServiceApi)
        Preview endpoints for settings not yet GA.
    beta_permissions (BetaInternalPermissionServiceApi)
        Preview endpoints for fine-grained permission management.
    beta_authorizations (BetaAuthorizationServiceApi)
        Preview endpoints for authorization workflows.
    beta_sessions (BetaSessionServiceApi)
        Preview endpoints for session features not yet GA.
    beta_instance (BetaInstanceServiceApi)
        Preview endpoints for instance-level operations.
    beta_telemetry (BetaTelemetryServiceApi)
        Preview endpoints for telemetry and observability.
    beta_features (BetaFeatureServiceApi)
        Preview endpoints for new feature toggles.
    beta_webkeys (BetaWebKeyServiceApi)
        Preview endpoints for WebCrypto keys in Beta.
    beta_actions (BetaActionServiceApi)
        Preview endpoints for custom action workflows.
    """

    def __init__(
        self,
        authenticator: Authenticator,
        mutate_config: Optional[Callable[[Configuration], None]] = None,
    ):
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
        self.saml = SAMLServiceApi(client)
        self.sessions = SessionServiceApi(client)
        self.settings = SettingsServiceApi(client)
        self.users = UserServiceApi(client)
        self.webkeys = WebKeyServiceApi(client)
        self.beta_projects = BetaProjectServiceApi(client)
        self.beta_apps = BetaAppServiceApi(client)
        self.beta_oidc = BetaOIDCServiceApi(client)
        self.beta_users = BetaUserServiceApi(client)
        self.beta_organizations = BetaOrganizationServiceApi(client)
        self.beta_settings = BetaSettingsServiceApi(client)
        self.beta_permissions = BetaInternalPermissionServiceApi(client)
        self.beta_authorizations = BetaAuthorizationServiceApi(client)
        self.beta_sessions = BetaSessionServiceApi(client)
        self.beta_instance = BetaInstanceServiceApi(client)
        self.beta_telemetry = BetaTelemetryServiceApi(client)
        self.beta_features = BetaFeatureServiceApi(client)
        self.beta_webkeys = BetaWebKeyServiceApi(client)
        self.beta_actions = BetaActionServiceApi(client)

    # noinspection PyArgumentList
    T = TypeVar("T", bound="Zitadel")

    def __enter__(self: T) -> T:
        """
        Enter the runtime context related to the Zitadel instance.

        Returns:
            Zitadel: The current instance.
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        """
        Exit the runtime context.

        This method can be used to perform cleanup actions. Currently, it does nothing.

        Args:
            exc_type: The exception type, if an exception occurred.
            exc_value: The exception value, if an exception occurred.
            traceback: The traceback of the exception, if an exception occurred.
        """
        pass

    @staticmethod
    def with_access_token(host: str, access_token: str) -> "Zitadel":
        """
        Initialize the SDK with a Personal Access Token (PAT).

        :param host: API URL (e.g., "https://api.zitadel.example.com").
        :param access_token: Personal Access Token for Bearer authentication.
        :return: Configured Zitadel client instance.
        :see: https://zitadel.com/docs/guides/integrate/service-users/personal-access-token
        """
        return Zitadel(PersonalAccessTokenAuthenticator(host, access_token))

    @staticmethod
    def with_client_credentials(host: str, client_id: str, client_secret: str) -> "Zitadel":
        """
        Initialize the SDK using OAuth2 Client Credentials flow.

        :param host: API URL.
        :param client_id: OAuth2 client identifier.
        :param client_secret: OAuth2 client secret.
        :return: Configured Zitadel client instance with token auto-refresh.
        :see: https://zitadel.com/docs/guides/integrate/service-users/client-credentials
        """
        return Zitadel(ClientCredentialsAuthenticator.builder(host, client_id, client_secret).build())

    @staticmethod
    def with_private_key(host: str, key_file: str) -> "Zitadel":
        """
        Initialize the SDK via Private Key JWT assertion.

        :param host: API URL.
        :param key_file: Path to service account JSON or PEM key file.
        :return: Configured Zitadel client instance using JWT assertion.
        :see: https://zitadel.com/docs/guides/integrate/service-users/private-key-jwt
        """
        return Zitadel(WebTokenAuthenticator.from_json(host, key_file))
