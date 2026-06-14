from types import TracebackType
from typing import Optional, Type, TypeVar

from zitadel_client.api.action_service_api import ActionServiceApi
from zitadel_client.api.application_service_api import ApplicationServiceApi
from zitadel_client.api.authorization_service_api import AuthorizationServiceApi
from zitadel_client.api.beta_action_service_api import BetaActionServiceApi
from zitadel_client.api.beta_app_service_api import BetaAppServiceApi
from zitadel_client.api.beta_authorization_service_api import (
    BetaAuthorizationServiceApi,
)
from zitadel_client.api.beta_feature_service_api import BetaFeatureServiceApi
from zitadel_client.api.beta_instance_service_api import BetaInstanceServiceApi
from zitadel_client.api.beta_internal_permission_service_api import (
    BetaInternalPermissionServiceApi,
)
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
from zitadel_client.api.instance_service_api import InstanceServiceApi
from zitadel_client.api.internal_permission_service_api import (
    InternalPermissionServiceApi,
)
from zitadel_client.api.oidc_service_api import OIDCServiceApi
from zitadel_client.api.organization_service_api import OrganizationServiceApi
from zitadel_client.api.project_service_api import ProjectServiceApi
from zitadel_client.api.saml_service_api import SAMLServiceApi
from zitadel_client.api.session_service_api import SessionServiceApi
from zitadel_client.api.settings_service_api import SettingsServiceApi
from zitadel_client.api.user_service_api import UserServiceApi
from zitadel_client.api.web_key_service_api import WebKeyServiceApi
from zitadel_client.auth.authenticator import Authenticator
from zitadel_client.auth.client_credentials_authenticator import (
    ClientCredentialsAuthenticator,
)
from zitadel_client.auth.http_aware_authenticator import HttpAwareAuthenticator
from zitadel_client.auth.personal_access_token_authenticator import (
    PersonalAccessTokenAuthenticator,
)
from zitadel_client.auth.web_token_authenticator import WebTokenAuthenticator
from zitadel_client.configuration import Configuration
from zitadel_client.default_api_client import DefaultApiClient
from zitadel_client.transport_options import TransportOptions


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
    actions (ActionServiceApi))
        Endpoints for custom action workflows.
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
        transport_options: Optional[TransportOptions] = None,
    ):
        """
        Initialize the Zitadel SDK.

        This constructor builds the shared API client from the supplied transport
        options and wires every service API to the given authenticator. If the
        authenticator implements :class:`HttpAwareAuthenticator`, the shared
        :class:`DefaultApiClient` is injected so that token exchange and discovery
        requests use the same proxy, TLS, and timeout settings as regular API calls.

        Args:
            authenticator (Authenticator): The authentication strategy to be used.
            transport_options (TransportOptions, optional): Transport configuration
                for TLS, proxy, and headers. Defaults to ``TransportOptions()``.
        """
        resolved = transport_options or TransportOptions()

        api_client = DefaultApiClient(resolved)

        if isinstance(authenticator, HttpAwareAuthenticator):
            authenticator.set_api_client(api_client)

        config = Configuration.builder().base_url(authenticator.get_host()).build()

        self.features = FeatureServiceApi(api_client, config, authenticator)
        self.idps = IdentityProviderServiceApi(api_client, config, authenticator)
        self.oidc = OIDCServiceApi(api_client, config, authenticator)
        self.organizations = OrganizationServiceApi(api_client, config, authenticator)
        self.saml = SAMLServiceApi(api_client, config, authenticator)
        self.sessions = SessionServiceApi(api_client, config, authenticator)
        self.settings = SettingsServiceApi(api_client, config, authenticator)
        self.users = UserServiceApi(api_client, config, authenticator)
        self.webkeys = WebKeyServiceApi(api_client, config, authenticator)
        self.actions = ActionServiceApi(api_client, config, authenticator)
        self.applications = ApplicationServiceApi(api_client, config, authenticator)
        self.authorizations = AuthorizationServiceApi(api_client, config, authenticator)
        self.beta_projects = BetaProjectServiceApi(api_client, config, authenticator)
        self.beta_apps = BetaAppServiceApi(api_client, config, authenticator)
        self.beta_oidc = BetaOIDCServiceApi(api_client, config, authenticator)
        self.beta_users = BetaUserServiceApi(api_client, config, authenticator)
        self.beta_organizations = BetaOrganizationServiceApi(
            api_client, config, authenticator
        )
        self.beta_settings = BetaSettingsServiceApi(api_client, config, authenticator)
        self.beta_permissions = BetaInternalPermissionServiceApi(
            api_client, config, authenticator
        )
        self.beta_authorizations = BetaAuthorizationServiceApi(
            api_client, config, authenticator
        )
        self.beta_sessions = BetaSessionServiceApi(api_client, config, authenticator)
        self.beta_instance = BetaInstanceServiceApi(api_client, config, authenticator)
        self.beta_telemetry = BetaTelemetryServiceApi(api_client, config, authenticator)
        self.instances = InstanceServiceApi(api_client, config, authenticator)
        self.internal_permissions = InternalPermissionServiceApi(
            api_client, config, authenticator
        )
        self.beta_features = BetaFeatureServiceApi(api_client, config, authenticator)
        self.beta_webkeys = BetaWebKeyServiceApi(api_client, config, authenticator)
        self.beta_actions = BetaActionServiceApi(api_client, config, authenticator)
        self.projects = ProjectServiceApi(api_client, config, authenticator)

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
        return None

    @staticmethod
    def with_access_token(
        host: str,
        access_token: str,
        *,
        transport_options: Optional[TransportOptions] = None,
    ) -> "Zitadel":
        """
        Initialize the SDK with a Personal Access Token (PAT).

        :param host: API URL (e.g., "https://api.zitadel.example.com").
        :param access_token: Personal Access Token for Bearer authentication.
        :param transport_options: Optional transport options for TLS, proxy, and headers.
        :return: Configured Zitadel client instance.
        :see: https://zitadel.com/docs/guides/integrate/service-users/personal-access-token
        """
        resolved = transport_options or TransportOptions()
        return Zitadel(
            PersonalAccessTokenAuthenticator(host, access_token),
            transport_options=resolved,
        )

    @staticmethod
    def with_client_credentials(
        host: str,
        client_id: str,
        client_secret: str,
        *,
        transport_options: Optional[TransportOptions] = None,
    ) -> "Zitadel":
        """
        Initialize the SDK using OAuth2 Client Credentials flow.

        :param host: API URL.
        :param client_id: OAuth2 client identifier.
        :param client_secret: OAuth2 client secret.
        :param transport_options: Optional transport options for TLS, proxy, and headers.
        :return: Configured Zitadel client instance with token auto-refresh.
        :see: https://zitadel.com/docs/guides/integrate/service-users/client-credentials
        """
        resolved = transport_options or TransportOptions()
        authenticator = ClientCredentialsAuthenticator.builder(
            host,
            client_id,
            client_secret,
            transport_options=resolved,
        ).build()
        return Zitadel(authenticator, transport_options=resolved)

    @staticmethod
    def with_private_key(
        host: str,
        key_file: str,
        *,
        transport_options: Optional[TransportOptions] = None,
    ) -> "Zitadel":
        """
        Initialize the SDK via Private Key JWT assertion.

        :param host: API URL.
        :param key_file: Path to service account JSON or PEM key file.
        :param transport_options: Optional transport options for TLS, proxy, and headers.
        :return: Configured Zitadel client instance using JWT assertion.
        :see: https://zitadel.com/docs/guides/integrate/service-users/private-key-jwt
        """
        resolved = transport_options or TransportOptions()
        authenticator = WebTokenAuthenticator.from_json(
            host,
            key_file,
            transport_options=resolved,
        )
        return Zitadel(authenticator, transport_options=resolved)
