from typing import Any, Dict, Optional

from zitadel_client.i_api_client import IApiClient
from zitadel_client.models.session_service_create_session_request import SessionServiceCreateSessionRequest
from zitadel_client.models.session_service_create_session_response import SessionServiceCreateSessionResponse
from zitadel_client.models.session_service_delete_session_request import SessionServiceDeleteSessionRequest
from zitadel_client.models.session_service_delete_session_response import SessionServiceDeleteSessionResponse
from zitadel_client.models.session_service_get_session_request import SessionServiceGetSessionRequest
from zitadel_client.models.session_service_get_session_response import SessionServiceGetSessionResponse
from zitadel_client.models.session_service_list_sessions_request import SessionServiceListSessionsRequest
from zitadel_client.models.session_service_list_sessions_response import SessionServiceListSessionsResponse
from zitadel_client.models.session_service_set_session_request import SessionServiceSetSessionRequest
from zitadel_client.models.session_service_set_session_response import SessionServiceSetSessionResponse

class SessionServiceApi:
    def __init__(self, api_client: IApiClient):
        self.api_client = api_client

    def create_session(
        self,
        session_service_create_session_request: SessionServiceCreateSessionRequest
    ) -> SessionServiceCreateSessionResponse:
        return self._create_session_internal(session_service_create_session_request, {})

    def _create_session_internal(
        self,
        session_service_create_session_request: SessionServiceCreateSessionRequest,
        additional_headers: Dict[str, Any]
    ) -> SessionServiceCreateSessionResponse:
        if session_service_create_session_request is None:
            raise ValueError("Missing the required parameter 'session_service_create_session_request' when calling create_session")

        return self.api_client.invoke_api(
            operation_id='create_session',
            path_template='/zitadel.session.v2.SessionService/CreateSession',
            method='POST',
            path_params={},
            query_params={},
            header_params=additional_headers,
            body=session_service_create_session_request,
            success_type=SessionServiceCreateSessionResponse
        )

    def delete_session(
        self,
        session_service_delete_session_request: SessionServiceDeleteSessionRequest
    ) -> SessionServiceDeleteSessionResponse:
        return self._delete_session_internal(session_service_delete_session_request, {})

    def _delete_session_internal(
        self,
        session_service_delete_session_request: SessionServiceDeleteSessionRequest,
        additional_headers: Dict[str, Any]
    ) -> SessionServiceDeleteSessionResponse:
        if session_service_delete_session_request is None:
            raise ValueError("Missing the required parameter 'session_service_delete_session_request' when calling delete_session")

        return self.api_client.invoke_api(
            operation_id='delete_session',
            path_template='/zitadel.session.v2.SessionService/DeleteSession',
            method='POST',
            path_params={},
            query_params={},
            header_params=additional_headers,
            body=session_service_delete_session_request,
            success_type=SessionServiceDeleteSessionResponse
        )

    def get_session(
        self,
        session_service_get_session_request: SessionServiceGetSessionRequest
    ) -> SessionServiceGetSessionResponse:
        return self._get_session_internal(session_service_get_session_request, {})

    def _get_session_internal(
        self,
        session_service_get_session_request: SessionServiceGetSessionRequest,
        additional_headers: Dict[str, Any]
    ) -> SessionServiceGetSessionResponse:
        if session_service_get_session_request is None:
            raise ValueError("Missing the required parameter 'session_service_get_session_request' when calling get_session")

        return self.api_client.invoke_api(
            operation_id='get_session',
            path_template='/zitadel.session.v2.SessionService/GetSession',
            method='POST',
            path_params={},
            query_params={},
            header_params=additional_headers,
            body=session_service_get_session_request,
            success_type=SessionServiceGetSessionResponse
        )

    def list_sessions(
        self,
        session_service_list_sessions_request: SessionServiceListSessionsRequest
    ) -> SessionServiceListSessionsResponse:
        return self._list_sessions_internal(session_service_list_sessions_request, {})

    def _list_sessions_internal(
        self,
        session_service_list_sessions_request: SessionServiceListSessionsRequest,
        additional_headers: Dict[str, Any]
    ) -> SessionServiceListSessionsResponse:
        if session_service_list_sessions_request is None:
            raise ValueError("Missing the required parameter 'session_service_list_sessions_request' when calling list_sessions")

        return self.api_client.invoke_api(
            operation_id='list_sessions',
            path_template='/zitadel.session.v2.SessionService/ListSessions',
            method='POST',
            path_params={},
            query_params={},
            header_params=additional_headers,
            body=session_service_list_sessions_request,
            success_type=SessionServiceListSessionsResponse
        )

    def set_session(
        self,
        session_service_set_session_request: SessionServiceSetSessionRequest
    ) -> SessionServiceSetSessionResponse:
        return self._set_session_internal(session_service_set_session_request, {})

    def _set_session_internal(
        self,
        session_service_set_session_request: SessionServiceSetSessionRequest,
        additional_headers: Dict[str, Any]
    ) -> SessionServiceSetSessionResponse:
        if session_service_set_session_request is None:
            raise ValueError("Missing the required parameter 'session_service_set_session_request' when calling set_session")

        return self.api_client.invoke_api(
            operation_id='set_session',
            path_template='/zitadel.session.v2.SessionService/SetSession',
            method='POST',
            path_params={},
            query_params={},
            header_params=additional_headers,
            body=session_service_set_session_request,
            success_type=SessionServiceSetSessionResponse
        )
