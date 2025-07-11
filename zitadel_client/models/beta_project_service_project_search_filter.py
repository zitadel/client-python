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
from zitadel_client.models.beta_project_service_id_filter import BetaProjectServiceIDFilter
from zitadel_client.models.beta_project_service_in_ids_filter import BetaProjectServiceInIDsFilter
from zitadel_client.models.beta_project_service_project_name_filter import BetaProjectServiceProjectNameFilter
from typing import Optional, Set
from typing_extensions import Self

class BetaProjectServiceProjectSearchFilter(BaseModel):
    """
    BetaProjectServiceProjectSearchFilter
    """ # noqa: E501
    in_project_ids_filter: Optional[BetaProjectServiceInIDsFilter] = Field(default=None, alias="inProjectIdsFilter")
    project_grant_resource_owner_filter: Optional[BetaProjectServiceIDFilter] = Field(default=None, alias="projectGrantResourceOwnerFilter")
    project_name_filter: Optional[BetaProjectServiceProjectNameFilter] = Field(default=None, alias="projectNameFilter")
    project_organization_id_filter: Optional[BetaProjectServiceIDFilter] = Field(default=None, alias="projectOrganizationIdFilter")
    project_resource_owner_filter: Optional[BetaProjectServiceIDFilter] = Field(default=None, alias="projectResourceOwnerFilter")
    __properties: ClassVar[List[str]] = ["inProjectIdsFilter", "projectGrantResourceOwnerFilter", "projectNameFilter", "projectOrganizationIdFilter", "projectResourceOwnerFilter"]

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
        """Create an instance of BetaProjectServiceProjectSearchFilter from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of in_project_ids_filter
        if self.in_project_ids_filter:
            _dict['inProjectIdsFilter'] = self.in_project_ids_filter.to_dict()
        # override the default output from pydantic by calling `to_dict()` of project_grant_resource_owner_filter
        if self.project_grant_resource_owner_filter:
            _dict['projectGrantResourceOwnerFilter'] = self.project_grant_resource_owner_filter.to_dict()
        # override the default output from pydantic by calling `to_dict()` of project_name_filter
        if self.project_name_filter:
            _dict['projectNameFilter'] = self.project_name_filter.to_dict()
        # override the default output from pydantic by calling `to_dict()` of project_organization_id_filter
        if self.project_organization_id_filter:
            _dict['projectOrganizationIdFilter'] = self.project_organization_id_filter.to_dict()
        # override the default output from pydantic by calling `to_dict()` of project_resource_owner_filter
        if self.project_resource_owner_filter:
            _dict['projectResourceOwnerFilter'] = self.project_resource_owner_filter.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of BetaProjectServiceProjectSearchFilter from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "inProjectIdsFilter": BetaProjectServiceInIDsFilter.from_dict(obj["inProjectIdsFilter"]) if obj.get("inProjectIdsFilter") is not None else None,
            "projectGrantResourceOwnerFilter": BetaProjectServiceIDFilter.from_dict(obj["projectGrantResourceOwnerFilter"]) if obj.get("projectGrantResourceOwnerFilter") is not None else None,
            "projectNameFilter": BetaProjectServiceProjectNameFilter.from_dict(obj["projectNameFilter"]) if obj.get("projectNameFilter") is not None else None,
            "projectOrganizationIdFilter": BetaProjectServiceIDFilter.from_dict(obj["projectOrganizationIdFilter"]) if obj.get("projectOrganizationIdFilter") is not None else None,
            "projectResourceOwnerFilter": BetaProjectServiceIDFilter.from_dict(obj["projectResourceOwnerFilter"]) if obj.get("projectResourceOwnerFilter") is not None else None
        })
        return _obj


