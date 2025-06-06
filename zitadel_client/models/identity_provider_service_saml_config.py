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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictBytes, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Union
from zitadel_client.models.identity_provider_service_saml_binding import IdentityProviderServiceSAMLBinding
from zitadel_client.models.identity_provider_service_saml_name_id_format import IdentityProviderServiceSAMLNameIDFormat
from typing import Optional, Set
from typing_extensions import Self

class IdentityProviderServiceSAMLConfig(BaseModel):
    """
    IdentityProviderServiceSAMLConfig
    """ # noqa: E501
    metadata_xml: Optional[Union[StrictBytes, StrictStr]] = Field(default=None, description="Metadata of the SAML identity provider.", alias="metadataXml")
    binding: Optional[IdentityProviderServiceSAMLBinding] = IdentityProviderServiceSAMLBinding.SAML_BINDING_UNSPECIFIED
    with_signed_request: Optional[StrictBool] = Field(default=None, description="Boolean which defines if the authentication requests are signed.", alias="withSignedRequest")
    name_id_format: Optional[IdentityProviderServiceSAMLNameIDFormat] = Field(default=IdentityProviderServiceSAMLNameIDFormat.SAML_NAME_ID_FORMAT_UNSPECIFIED, alias="nameIdFormat")
    transient_mapping_attribute_name: Optional[StrictStr] = Field(default=None, description="Optional name of the attribute, which will be used to map the user in case the nameid-format returned is `urn:oasis:names:tc:SAML:2.0:nameid-format:transient`.", alias="transientMappingAttributeName")
    federated_logout_enabled: Optional[StrictBool] = Field(default=None, description="Boolean weather federated logout is enabled. If enabled, ZITADEL will send a logout request to the identity provider, if the user terminates the session in ZITADEL. Be sure to provide a SLO endpoint as part of the metadata.", alias="federatedLogoutEnabled")

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
        """Create an instance of IdentityProviderServiceSAMLConfig from a JSON string"""
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
        """Create an instance of IdentityProviderServiceSAMLConfig from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "metadataXml": obj.get("metadataXml"),
            "binding": obj.get("binding") if obj.get("binding") is not None else IdentityProviderServiceSAMLBinding.SAML_BINDING_UNSPECIFIED,
            "withSignedRequest": obj.get("withSignedRequest"),
            "nameIdFormat": obj.get("nameIdFormat") if obj.get("nameIdFormat") is not None else IdentityProviderServiceSAMLNameIDFormat.SAML_NAME_ID_FORMAT_UNSPECIFIED,
            "transientMappingAttributeName": obj.get("transientMappingAttributeName"),
            "federatedLogoutEnabled": obj.get("federatedLogoutEnabled")
        })
        return _obj


