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


class BetaProjectServiceProjectFieldName(str, Enum):
    """
    BetaProjectServiceProjectFieldName
    """

    """
    allowed enum values
    """
    PROJECT_FIELD_NAME_UNSPECIFIED = 'PROJECT_FIELD_NAME_UNSPECIFIED'
    PROJECT_FIELD_NAME_ID = 'PROJECT_FIELD_NAME_ID'
    PROJECT_FIELD_NAME_CREATION_DATE = 'PROJECT_FIELD_NAME_CREATION_DATE'
    PROJECT_FIELD_NAME_CHANGE_DATE = 'PROJECT_FIELD_NAME_CHANGE_DATE'
    PROJECT_FIELD_NAME_NAME = 'PROJECT_FIELD_NAME_NAME'

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of BetaProjectServiceProjectFieldName from a JSON string"""
        return cls(json.loads(json_str))


