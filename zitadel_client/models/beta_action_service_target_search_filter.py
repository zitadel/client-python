# coding: utf-8

"""
    Zitadel SDK

    The Zitadel SDK is a convenience wrapper around the Zitadel APIs to assist you in integrating with your Zitadel environment. This SDK enables you to handle resources, settings, and configurations within the Zitadel platform.

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, ClassVar, Dict, Optional
from zitadel_client.models.beta_action_service_in_target_ids_filter import BetaActionServiceInTargetIDsFilter
from zitadel_client.models.beta_action_service_target_name_filter import BetaActionServiceTargetNameFilter
from typing import Optional, Set
from typing_extensions import Self

class BetaActionServiceTargetSearchFilter(BaseModel):
    """
    BetaActionServiceTargetSearchFilter
    """ # noqa: E501
    in_target_ids_filter: Optional[BetaActionServiceInTargetIDsFilter] = Field(default=None, alias="inTargetIdsFilter")
    target_name_filter: Optional[BetaActionServiceTargetNameFilter] = Field(default=None, alias="targetNameFilter")
    __properties: ClassVar[List[str]] = ["inTargetIdsFilter", "targetNameFilter"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of BetaActionServiceTargetSearchFilter from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of in_target_ids_filter
        if self.in_target_ids_filter:
            _dict['inTargetIdsFilter'] = self.in_target_ids_filter.to_dict()
        # override the default output from pydantic by calling `to_dict()` of target_name_filter
        if self.target_name_filter:
            _dict['targetNameFilter'] = self.target_name_filter.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of BetaActionServiceTargetSearchFilter from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "inTargetIdsFilter": BetaActionServiceInTargetIDsFilter.from_dict(obj["inTargetIdsFilter"]) if obj.get("inTargetIdsFilter") is not None else None,
            "targetNameFilter": BetaActionServiceTargetNameFilter.from_dict(obj["targetNameFilter"]) if obj.get("targetNameFilter") is not None else None
        })
        return _obj


