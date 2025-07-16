from typing import Any, Dict, Optional

from zitadel_client.i_api_client import IApiClient
from zitadel_client.models.user_service_add_human_user_request import UserServiceAddHumanUserRequest
from zitadel_client.models.user_service_add_human_user_response import UserServiceAddHumanUserResponse
from zitadel_client.models.user_service_delete_user_request import UserServiceDeleteUserRequest
from zitadel_client.models.user_service_delete_user_response import UserServiceDeleteUserResponse
from zitadel_client.models.user_service_get_user_by_id_request import UserServiceGetUserByIDRequest
from zitadel_client.models.user_service_get_user_by_id_response import UserServiceGetUserByIDResponse
from zitadel_client.models.user_service_list_users_request import UserServiceListUsersRequest
from zitadel_client.models.user_service_list_users_response import UserServiceListUsersResponse
from zitadel_client.models.user_service_update_human_user_request import UserServiceUpdateHumanUserRequest
from zitadel_client.models.user_service_update_human_user_response import UserServiceUpdateHumanUserResponse

class UserServiceApi:
    def __init__(self, api_client: IApiClient):
        self.api_client = api_client

    def add_human_user(
        self,
        user_service_add_human_user_request: UserServiceAddHumanUserRequest
    ) -> UserServiceAddHumanUserResponse:
        return self._add_human_user_internal(user_service_add_human_user_request, {})

    def _add_human_user_internal(
        self,
        user_service_add_human_user_request: UserServiceAddHumanUserRequest,
        additional_headers: Dict[str, Any]
    ) -> UserServiceAddHumanUserResponse:
        if user_service_add_human_user_request is None:
            raise ValueError("Missing the required parameter 'user_service_add_human_user_request' when calling add_human_user")

        return self.api_client.invoke_api(
            operation_id='add_human_user',
            path_template='/zitadel.user.v2.UserService/AddHumanUser',
            method='POST',
            path_params={},
            query_params={},
            header_params=additional_headers,
            body=user_service_add_human_user_request,
            success_type=UserServiceAddHumanUserResponse
        )

    def delete_user(
        self,
        user_service_delete_user_request: UserServiceDeleteUserRequest
    ) -> UserServiceDeleteUserResponse:
        return self._delete_user_internal(user_service_delete_user_request, {})

    def _delete_user_internal(
        self,
        user_service_delete_user_request: UserServiceDeleteUserRequest,
        additional_headers: Dict[str, Any]
    ) -> UserServiceDeleteUserResponse:
        if user_service_delete_user_request is None:
            raise ValueError("Missing the required parameter 'user_service_delete_user_request' when calling delete_user")

        return self.api_client.invoke_api(
            operation_id='delete_user',
            path_template='/zitadel.user.v2.UserService/DeleteUser',
            method='POST',
            path_params={},
            query_params={},
            header_params=additional_headers,
            body=user_service_delete_user_request,
            success_type=UserServiceDeleteUserResponse
        )

    def get_user_by_id(
        self,
        user_service_get_user_by_id_request: UserServiceGetUserByIDRequest
    ) -> UserServiceGetUserByIDResponse:
        return self._get_user_by_id_internal(user_service_get_user_by_id_request, {})

    def _get_user_by_id_internal(
        self,
        user_service_get_user_by_id_request: UserServiceGetUserByIDRequest,
        additional_headers: Dict[str, Any]
    ) -> UserServiceGetUserByIDResponse:
        if user_service_get_user_by_id_request is None:
            raise ValueError("Missing the required parameter 'user_service_get_user_by_id_request' when calling get_user_by_id")

        return self.api_client.invoke_api(
            operation_id='get_user_by_id',
            path_template='/zitadel.user.v2.UserService/GetUserByID',
            method='POST',
            path_params={},
            query_params={},
            header_params=additional_headers,
            body=user_service_get_user_by_id_request,
            success_type=UserServiceGetUserByIDResponse
        )

    def list_users(
        self,
        user_service_list_users_request: UserServiceListUsersRequest
    ) -> UserServiceListUsersResponse:
        return self._list_users_internal(user_service_list_users_request, {})

    def _list_users_internal(
        self,
        user_service_list_users_request: UserServiceListUsersRequest,
        additional_headers: Dict[str, Any]
    ) -> UserServiceListUsersResponse:
        if user_service_list_users_request is None:
            raise ValueError("Missing the required parameter 'user_service_list_users_request' when calling list_users")

        return self.api_client.invoke_api(
            operation_id='list_users',
            path_template='/zitadel.user.v2.UserService/ListUsers',
            method='POST',
            path_params={},
            query_params={},
            header_params=additional_headers,
            body=user_service_list_users_request,
            success_type=UserServiceListUsersResponse
        )

    def update_human_user(
        self,
        user_service_update_human_user_request: UserServiceUpdateHumanUserRequest
    ) -> UserServiceUpdateHumanUserResponse:
        return self._update_human_user_internal(user_service_update_human_user_request, {})

    def _update_human_user_internal(
        self,
        user_service_update_human_user_request: UserServiceUpdateHumanUserRequest,
        additional_headers: Dict[str, Any]
    ) -> UserServiceUpdateHumanUserResponse:
        if user_service_update_human_user_request is None:
            raise ValueError("Missing the required parameter 'user_service_update_human_user_request' when calling update_human_user")

        return self.api_client.invoke_api(
            operation_id='update_human_user',
            path_template='/zitadel.user.v2.UserService/UpdateHumanUser',
            method='POST',
            path_params={},
            query_params={},
            header_params=additional_headers,
            body=user_service_update_human_user_request,
            success_type=UserServiceUpdateHumanUserResponse
        )
