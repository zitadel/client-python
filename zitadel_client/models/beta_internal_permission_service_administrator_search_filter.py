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
from zitadel_client.models.beta_internal_permission_service_id_filter import BetaInternalPermissionServiceIDFilter
from zitadel_client.models.beta_internal_permission_service_in_ids_filter import BetaInternalPermissionServiceInIDsFilter
from zitadel_client.models.beta_internal_permission_service_resource_filter import BetaInternalPermissionServiceResourceFilter
from zitadel_client.models.beta_internal_permission_service_role_filter import BetaInternalPermissionServiceRoleFilter
from zitadel_client.models.beta_internal_permission_service_timestamp_filter import BetaInternalPermissionServiceTimestampFilter
from zitadel_client.models.beta_internal_permission_service_user_display_name_filter import BetaInternalPermissionServiceUserDisplayNameFilter
from zitadel_client.models.beta_internal_permission_service_user_preferred_login_name_filter import BetaInternalPermissionServiceUserPreferredLoginNameFilter
from typing import Optional, Set
from typing_extensions import Self

class BetaInternalPermissionServiceAdministratorSearchFilter(BaseModel):
    """
    BetaInternalPermissionServiceAdministratorSearchFilter
    """ # noqa: E501
    var_and: Optional[BetaInternalPermissionServiceAndFilter] = Field(default=None, alias="and")
    change_date: Optional[BetaInternalPermissionServiceTimestampFilter] = Field(default=None, alias="changeDate")
    creation_date: Optional[BetaInternalPermissionServiceTimestampFilter] = Field(default=None, alias="creationDate")
    in_user_ids_filter: Optional[BetaInternalPermissionServiceInIDsFilter] = Field(default=None, alias="inUserIdsFilter")
    var_not: Optional[BetaInternalPermissionServiceNotFilter] = Field(default=None, alias="not")
    var_or: Optional[BetaInternalPermissionServiceOrFilter] = Field(default=None, alias="or")
    resource: Optional[BetaInternalPermissionServiceResourceFilter] = None
    role: Optional[BetaInternalPermissionServiceRoleFilter] = None
    user_display_name: Optional[BetaInternalPermissionServiceUserDisplayNameFilter] = Field(default=None, alias="userDisplayName")
    user_organization_id: Optional[BetaInternalPermissionServiceIDFilter] = Field(default=None, alias="userOrganizationId")
    user_preferred_login_name: Optional[BetaInternalPermissionServiceUserPreferredLoginNameFilter] = Field(default=None, alias="userPreferredLoginName")
    __properties: ClassVar[List[str]] = ["and", "changeDate", "creationDate", "inUserIdsFilter", "not", "or", "resource", "role", "userDisplayName", "userOrganizationId", "userPreferredLoginName"]

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
        """Create an instance of BetaInternalPermissionServiceAdministratorSearchFilter from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of var_and
        if self.var_and:
            _dict['and'] = self.var_and.to_dict()
        # override the default output from pydantic by calling `to_dict()` of change_date
        if self.change_date:
            _dict['changeDate'] = self.change_date.to_dict()
        # override the default output from pydantic by calling `to_dict()` of creation_date
        if self.creation_date:
            _dict['creationDate'] = self.creation_date.to_dict()
        # override the default output from pydantic by calling `to_dict()` of in_user_ids_filter
        if self.in_user_ids_filter:
            _dict['inUserIdsFilter'] = self.in_user_ids_filter.to_dict()
        # override the default output from pydantic by calling `to_dict()` of var_not
        if self.var_not:
            _dict['not'] = self.var_not.to_dict()
        # override the default output from pydantic by calling `to_dict()` of var_or
        if self.var_or:
            _dict['or'] = self.var_or.to_dict()
        # override the default output from pydantic by calling `to_dict()` of resource
        if self.resource:
            _dict['resource'] = self.resource.to_dict()
        # override the default output from pydantic by calling `to_dict()` of role
        if self.role:
            _dict['role'] = self.role.to_dict()
        # override the default output from pydantic by calling `to_dict()` of user_display_name
        if self.user_display_name:
            _dict['userDisplayName'] = self.user_display_name.to_dict()
        # override the default output from pydantic by calling `to_dict()` of user_organization_id
        if self.user_organization_id:
            _dict['userOrganizationId'] = self.user_organization_id.to_dict()
        # override the default output from pydantic by calling `to_dict()` of user_preferred_login_name
        if self.user_preferred_login_name:
            _dict['userPreferredLoginName'] = self.user_preferred_login_name.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of BetaInternalPermissionServiceAdministratorSearchFilter from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "and": BetaInternalPermissionServiceAndFilter.from_dict(obj["and"]) if obj.get("and") is not None else None,
            "changeDate": BetaInternalPermissionServiceTimestampFilter.from_dict(obj["changeDate"]) if obj.get("changeDate") is not None else None,
            "creationDate": BetaInternalPermissionServiceTimestampFilter.from_dict(obj["creationDate"]) if obj.get("creationDate") is not None else None,
            "inUserIdsFilter": BetaInternalPermissionServiceInIDsFilter.from_dict(obj["inUserIdsFilter"]) if obj.get("inUserIdsFilter") is not None else None,
            "not": BetaInternalPermissionServiceNotFilter.from_dict(obj["not"]) if obj.get("not") is not None else None,
            "or": BetaInternalPermissionServiceOrFilter.from_dict(obj["or"]) if obj.get("or") is not None else None,
            "resource": BetaInternalPermissionServiceResourceFilter.from_dict(obj["resource"]) if obj.get("resource") is not None else None,
            "role": BetaInternalPermissionServiceRoleFilter.from_dict(obj["role"]) if obj.get("role") is not None else None,
            "userDisplayName": BetaInternalPermissionServiceUserDisplayNameFilter.from_dict(obj["userDisplayName"]) if obj.get("userDisplayName") is not None else None,
            "userOrganizationId": BetaInternalPermissionServiceIDFilter.from_dict(obj["userOrganizationId"]) if obj.get("userOrganizationId") is not None else None,
            "userPreferredLoginName": BetaInternalPermissionServiceUserPreferredLoginNameFilter.from_dict(obj["userPreferredLoginName"]) if obj.get("userPreferredLoginName") is not None else None
        })
        return _obj

from zitadel_client.models.beta_internal_permission_service_and_filter import BetaInternalPermissionServiceAndFilter
from zitadel_client.models.beta_internal_permission_service_not_filter import BetaInternalPermissionServiceNotFilter
from zitadel_client.models.beta_internal_permission_service_or_filter import BetaInternalPermissionServiceOrFilter
# TODO: Rewrite to not use raise_errors
BetaInternalPermissionServiceAdministratorSearchFilter.model_rebuild(raise_errors=False)

