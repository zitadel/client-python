# coding: utf-8

"""
    Zitadel SDK

    The Zitadel SDK is a convenience wrapper around the Zitadel APIs to assist you in integrating with your Zitadel environment. This SDK enables you to handle resources, settings, and configurations within the Zitadel platform.

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501

import warnings
from pydantic import validate_call, Field, StrictFloat, StrictStr, StrictInt
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated

from pydantic import Field, StrictStr
from typing_extensions import Annotated
from zitadel_client.models.saml_service_create_response_request import SAMLServiceCreateResponseRequest
from zitadel_client.models.saml_service_create_response_response import SAMLServiceCreateResponseResponse
from zitadel_client.models.saml_service_get_saml_request_response import SAMLServiceGetSAMLRequestResponse

from zitadel_client.api_client import ApiClient, RequestSerialized
from zitadel_client.api_response import ApiResponse
from zitadel_client.rest import RESTResponseType


class SAMLServiceApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def s_aml_service_create_response(
    self,
      saml_request_id: Annotated[StrictStr, Field(description="ID of the SAML Request.")],
      saml_service_create_response_request: SAMLServiceCreateResponseRequest,
    ) -> SAMLServiceCreateResponseResponse:
        """Finalize a SAML Request and get the response.

        Finalize a SAML Request and get the response definition for success or failure. The response must be handled as per the SAML definition to inform the application about the success or failure. On success, the response contains details for the application to obtain the SAMLResponse. This method can only be called once for an SAML request.

        :param saml_request_id: ID of the SAML Request. (required)
        :type saml_request_id: str
        :param saml_service_create_response_request: (required)
        :type saml_service_create_response_request: SAMLServiceCreateResponseRequest
        :return: Returns the result object.
        """ # noqa: E501

        _param = self.__s_aml_service_create_response_serialize(
            saml_request_id=saml_request_id,
            saml_service_create_response_request=saml_service_create_response_request,
            _request_auth=None,
            _content_type=None,
            _headers=None,
            _host_index=0
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "SAMLServiceCreateResponseResponse",
            '403': "SAMLServiceRpcStatus",
            '404': "SAMLServiceRpcStatus",
        }

        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=None
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data

    def __s_aml_service_create_response_serialize(
        self,
        saml_request_id,
        saml_service_create_response_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if saml_request_id is not None:
            _path_params['samlRequestId'] = saml_request_id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if saml_service_create_response_request is not None:
            _body_params = saml_service_create_response_request


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'zitadelAccessToken'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/v2/saml/saml_requests/{samlRequestId}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def s_aml_service_get_saml_request(
    self,
      saml_request_id: Annotated[StrictStr, Field(description="ID of the SAML Request, as obtained from the redirect URL.")],
    ) -> SAMLServiceGetSAMLRequestResponse:
        """Get SAML Request details

        Get SAML Request details by ID. Returns details that are parsed from the application's SAML Request.

        :param saml_request_id: ID of the SAML Request, as obtained from the redirect URL. (required)
        :type saml_request_id: str
        :return: Returns the result object.
        """ # noqa: E501

        _param = self.__s_aml_service_get_saml_request_serialize(
            saml_request_id=saml_request_id,
            _request_auth=None,
            _content_type=None,
            _headers=None,
            _host_index=0
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "SAMLServiceGetSAMLRequestResponse",
            '403': "SAMLServiceRpcStatus",
            '404': "SAMLServiceRpcStatus",
        }

        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=None
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data

    def __s_aml_service_get_saml_request_serialize(
        self,
        saml_request_id,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if saml_request_id is not None:
            _path_params['samlRequestId'] = saml_request_id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'zitadelAccessToken'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v2/saml/saml_requests/{samlRequestId}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )


