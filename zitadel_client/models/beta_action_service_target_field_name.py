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


class BetaActionServiceTargetFieldName(str, Enum):
    """
    BetaActionServiceTargetFieldName
    """

    """
    allowed enum values
    """
    TARGET_FIELD_NAME_UNSPECIFIED = 'TARGET_FIELD_NAME_UNSPECIFIED'
    TARGET_FIELD_NAME_ID = 'TARGET_FIELD_NAME_ID'
    TARGET_FIELD_NAME_CREATED_DATE = 'TARGET_FIELD_NAME_CREATED_DATE'
    TARGET_FIELD_NAME_CHANGED_DATE = 'TARGET_FIELD_NAME_CHANGED_DATE'
    TARGET_FIELD_NAME_NAME = 'TARGET_FIELD_NAME_NAME'
    TARGET_FIELD_NAME_TARGET_TYPE = 'TARGET_FIELD_NAME_TARGET_TYPE'
    TARGET_FIELD_NAME_URL = 'TARGET_FIELD_NAME_URL'
    TARGET_FIELD_NAME_TIMEOUT = 'TARGET_FIELD_NAME_TIMEOUT'
    TARGET_FIELD_NAME_INTERRUPT_ON_ERROR = 'TARGET_FIELD_NAME_INTERRUPT_ON_ERROR'

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of BetaActionServiceTargetFieldName from a JSON string"""
        return cls(json.loads(json_str))


