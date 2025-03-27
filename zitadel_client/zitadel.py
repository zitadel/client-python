from zitadel_client.api.feature_service_api import FeatureServiceApi
from zitadel_client.api.identity_provider_service_api import IdentityProviderServiceApi
from zitadel_client.api.oidc_service_api import OIDCServiceApi
from zitadel_client.api.organization_service_api import OrganizationServiceApi
from zitadel_client.api.session_service_api import SessionServiceApi
from zitadel_client.api.settings_api import SettingsApi
from zitadel_client.api.settings_service_api import SettingsServiceApi
from zitadel_client.api.user_service_api import UserServiceApi
from zitadel_client.configuration import Configuration
from zitadel_client.api_client import ApiClient

class Zitadel:
	def __init__(self, host: str, access_token: str):
		"""
		Initialize the Zitadel SDK with the provided host and access token.

		Parameters:
		- host: The base URL of the Zitadel API.
		- access_token: The access token for authenticating API requests.
		"""
		self.configuration = Configuration(
			host = host,
			access_token = access_token
		)

		self.client = ApiClient(configuration = self.configuration)
		self.features = FeatureServiceApi(self.client)
		self.idps = IdentityProviderServiceApi(self.client)
		self.oidc = OIDCServiceApi(self.client)
		self.organizations = OrganizationServiceApi(self.client)
		self.sessions = SessionServiceApi(self.client)
		self.settings = SettingsServiceApi(self.client)
		self.users = UserServiceApi(self.client)

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		pass
