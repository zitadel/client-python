from zitadel_client.i_api_client import IApiClient


class BetaOrganizationServiceApi:
    def __init__(self, api_client: IApiClient) -> None:
        self.api_client = api_client
