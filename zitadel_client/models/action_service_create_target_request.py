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
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from zitadel_client.models.action_service_beta_rest_call import ActionServiceBetaRESTCall
from zitadel_client.models.action_service_beta_rest_webhook import ActionServiceBetaRESTWebhook
from typing import Optional, Set
from typing_extensions import Self

class ActionServiceCreateTargetRequest(BaseModel):
    """
    ActionServiceCreateTargetRequest
    """ # noqa: E501
    name: Optional[Annotated[str, Field(min_length=1, strict=True, max_length=1000)]] = None
    rest_webhook: Optional[ActionServiceBetaRESTWebhook] = Field(default=None, alias="restWebhook")
    rest_call: Optional[ActionServiceBetaRESTCall] = Field(default=None, alias="restCall")
    rest_async: Optional[Dict[str, Any]] = Field(default=None, alias="restAsync")
    timeout: Optional[StrictStr] = Field(default=None, description="Timeout defines the duration until ZITADEL cancels the execution. If the target doesn't respond before this timeout expires, then the connection is closed and the action fails. Depending on the target type and possible setting on `interrupt_on_error` following targets will not be called. In case of a `rest_async` target only this specific target will fail, without any influence on other targets of the same execution.")
    endpoint: Optional[Annotated[str, Field(min_length=1, strict=True, max_length=1000)]] = None

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
        """Create an instance of ActionServiceCreateTargetRequest from a JSON string"""
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
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ActionServiceCreateTargetRequest from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "name": obj.get("name"),
            "restWebhook": ActionServiceBetaRESTWebhook.from_dict(obj["restWebhook"]) if obj.get("restWebhook") is not None else None,
            "restCall": ActionServiceBetaRESTCall.from_dict(obj["restCall"]) if obj.get("restCall") is not None else None,
            "restAsync": obj.get("restAsync"),
            "timeout": obj.get("timeout"),
            "endpoint": obj.get("endpoint")
        })
        return _obj


