from typing import Any, Dict, Optional

from zitadel_client.i_api_client import IApiClient
from zitadel_client.models.settings_service_get_general_settings_response import SettingsServiceGetGeneralSettingsResponse
from zitadel_client.models.settings_service_get_login_settings_request import SettingsServiceGetLoginSettingsRequest
from zitadel_client.models.settings_service_get_login_settings_response import SettingsServiceGetLoginSettingsResponse

class SettingsServiceApi:
    def __init__(self, api_client: IApiClient):
        self.api_client = api_client

    def get_general_settings(
        self,
        body: Optional[Dict[str, Any]] = None
    ) -> SettingsServiceGetGeneralSettingsResponse:
        return self._get_general_settings_internal(body, {})

    def _get_general_settings_internal(
        self,
        body: Optional[Dict[str, Any]],
        additional_headers: Dict[str, Any]
    ) -> SettingsServiceGetGeneralSettingsResponse:
        if body is None:
            body = {}

        return self.api_client.invoke_api(
            operation_id='get_general_settings',
            path_template='/zitadel.settings.v2.SettingsService/GetGeneralSettings',
            method='POST',
            path_params={},
            query_params={},
            header_params=additional_headers,
            body=body,
            success_type=SettingsServiceGetGeneralSettingsResponse
        )

    def get_login_settings(
        self,
        settings_service_get_login_settings_request: SettingsServiceGetLoginSettingsRequest
    ) -> SettingsServiceGetLoginSettingsResponse:
        return self._get_login_settings_internal(settings_service_get_login_settings_request, {})

    def _get_login_settings_internal(
        self,
        settings_service_get_login_settings_request: SettingsServiceGetLoginSettingsRequest,
        additional_headers: Dict[str, Any]
    ) -> SettingsServiceGetLoginSettingsResponse:
        if settings_service_get_login_settings_request is None:
            raise ValueError("Missing the required parameter 'settings_service_get_login_settings_request' when calling get_login_settings")

        return self.api_client.invoke_api(
            operation_id='get_login_settings',
            path_template='/zitadel.settings.v2.SettingsService/GetLoginSettings',
            method='POST',
            path_params={},
            query_params={},
            header_params=additional_headers,
            body=settings_service_get_login_settings_request,
            success_type=SettingsServiceGetLoginSettingsResponse
        )
