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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr
from typing import Any, ClassVar, Dict, Optional
from zitadel_client.models.beta_user_service_send_email_verification_code import BetaUserServiceSendEmailVerificationCode
from typing import Optional, Set
from typing_extensions import Self

class BetaUserServiceSetEmailRequest(BaseModel):
    """
    BetaUserServiceSetEmailRequest
    """ # noqa: E501
    user_id: StrictStr = Field(alias="userId")
    email: StrictStr
    is_verified: Optional[StrictBool] = Field(default=None, alias="isVerified")
    return_code: Optional[Dict[str, Any]] = Field(default=None, alias="returnCode")
    send_code: Optional[BetaUserServiceSendEmailVerificationCode] = Field(default=None, alias="sendCode")
    __properties: ClassVar[List[str]] = ["userId", "email", "isVerified", "returnCode", "sendCode"]

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
        """Create an instance of BetaUserServiceSetEmailRequest from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of send_code
        if self.send_code:
            _dict['sendCode'] = self.send_code.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of BetaUserServiceSetEmailRequest from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "userId": obj.get("userId"),
            "email": obj.get("email"),
            "isVerified": obj.get("isVerified"),
            "returnCode": obj.get("returnCode"),
            "sendCode": BetaUserServiceSendEmailVerificationCode.from_dict(obj["sendCode"]) if obj.get("sendCode") is not None else None
        })
        return _obj


