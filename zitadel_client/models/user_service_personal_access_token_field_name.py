# coding: utf-8

"""
    Zitadel SDK

    The Zitadel SDK is a convenience wrapper around the Zitadel APIs to assist you in integrating with your Zitadel environment. This SDK enables you to handle resources, settings, and configurations within the Zitadel platform.

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import json
from enum import Enum
from typing_extensions import Self


class UserServicePersonalAccessTokenFieldName(str, Enum):
    """
    UserServicePersonalAccessTokenFieldName
    """

    """
    allowed enum values
    """
    PERSONAL_ACCESS_TOKEN_FIELD_NAME_UNSPECIFIED = 'PERSONAL_ACCESS_TOKEN_FIELD_NAME_UNSPECIFIED'
    PERSONAL_ACCESS_TOKEN_FIELD_NAME_CREATED_DATE = 'PERSONAL_ACCESS_TOKEN_FIELD_NAME_CREATED_DATE'
    PERSONAL_ACCESS_TOKEN_FIELD_NAME_ID = 'PERSONAL_ACCESS_TOKEN_FIELD_NAME_ID'
    PERSONAL_ACCESS_TOKEN_FIELD_NAME_USER_ID = 'PERSONAL_ACCESS_TOKEN_FIELD_NAME_USER_ID'
    PERSONAL_ACCESS_TOKEN_FIELD_NAME_ORGANIZATION_ID = 'PERSONAL_ACCESS_TOKEN_FIELD_NAME_ORGANIZATION_ID'
    PERSONAL_ACCESS_TOKEN_FIELD_NAME_EXPIRATION_DATE = 'PERSONAL_ACCESS_TOKEN_FIELD_NAME_EXPIRATION_DATE'

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of UserServicePersonalAccessTokenFieldName from a JSON string"""
        return cls(json.loads(json_str))


