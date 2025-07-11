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
from zitadel_client.models.session_service_web_auth_n import SessionServiceWebAuthN
from typing import Optional, Set
from typing_extensions import Self

class SessionServiceChallenges(BaseModel):
    """
    SessionServiceChallenges
    """ # noqa: E501
    web_auth_n: Optional[SessionServiceWebAuthN] = Field(default=None, alias="webAuthN")
    otp_sms: Optional[StrictStr] = Field(default=None, alias="otpSms")
    otp_email: Optional[StrictStr] = Field(default=None, alias="otpEmail")
    __properties: ClassVar[List[str]] = ["webAuthN", "otpSms", "otpEmail"]

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
        """Create an instance of SessionServiceChallenges from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of web_auth_n
        if self.web_auth_n:
            _dict['webAuthN'] = self.web_auth_n.to_dict()
        # set to None if otp_sms (nullable) is None
        # and model_fields_set contains the field
        if self.otp_sms is None and "otp_sms" in self.model_fields_set:
            _dict['otpSms'] = None

        # set to None if otp_email (nullable) is None
        # and model_fields_set contains the field
        if self.otp_email is None and "otp_email" in self.model_fields_set:
            _dict['otpEmail'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of SessionServiceChallenges from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "webAuthN": SessionServiceWebAuthN.from_dict(obj["webAuthN"]) if obj.get("webAuthN") is not None else None,
            "otpSms": obj.get("otpSms"),
            "otpEmail": obj.get("otpEmail")
        })
        return _obj


