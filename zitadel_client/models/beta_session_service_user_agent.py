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

from pydantic import BaseModel, ConfigDict, Field, StrictStr
from typing import Any, ClassVar, Dict, Optional
from zitadel_client.models.beta_session_service_header_values import BetaSessionServiceHeaderValues
from typing import Optional, Set
from typing_extensions import Self

class BetaSessionServiceUserAgent(BaseModel):
    """
    BetaSessionServiceUserAgent
    """ # noqa: E501
    fingerprint_id: Optional[StrictStr] = Field(default=None, alias="fingerprintId")
    ip: Optional[StrictStr] = None
    description: Optional[StrictStr] = None
    header: Optional[Dict[str, BetaSessionServiceHeaderValues]] = None
    __properties: ClassVar[List[str]] = ["fingerprintId", "ip", "description", "header"]

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
        """Create an instance of BetaSessionServiceUserAgent from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each value in header (dict)
        _field_dict = {}
        if self.header:
            for _key_header in self.header:
                if self.header[_key_header]:
                    _field_dict[_key_header] = self.header[_key_header].to_dict()
            _dict['header'] = _field_dict
        # set to None if fingerprint_id (nullable) is None
        # and model_fields_set contains the field
        if self.fingerprint_id is None and "fingerprint_id" in self.model_fields_set:
            _dict['fingerprintId'] = None

        # set to None if ip (nullable) is None
        # and model_fields_set contains the field
        if self.ip is None and "ip" in self.model_fields_set:
            _dict['ip'] = None

        # set to None if description (nullable) is None
        # and model_fields_set contains the field
        if self.description is None and "description" in self.model_fields_set:
            _dict['description'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of BetaSessionServiceUserAgent from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "fingerprintId": obj.get("fingerprintId"),
            "ip": obj.get("ip"),
            "description": obj.get("description"),
            "header": dict(
                (_k, BetaSessionServiceHeaderValues.from_dict(_v))
                for _k, _v in obj["header"].items()
            )
            if obj.get("header") is not None
            else None
        })
        return _obj


