import json
import unittest
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from zitadel_client.object_serializer import ObjectSerializer


class SerdeModel(BaseModel):
    some_string: Optional[str] = Field(default=None, alias="some_string")
    some_binary: Optional[str] = Field(default=None, alias="some_binary")
    some_byte: Optional[str] = Field(default=None, alias="some_byte")
    some_date: Optional[date] = Field(default=None, alias="some_date")
    some_date_time: Optional[datetime] = Field(default=None, alias="some_date_time")
    some_password: Optional[str] = Field(default=None, alias="some_password")
    some_email: Optional[str] = Field(default=None, alias="some_email")
    some_hostname: Optional[str] = Field(default=None, alias="some_hostname")
    some_ipv4: Optional[str] = Field(default=None, alias="some_ipv4")
    some_ipv6: Optional[str] = Field(default=None, alias="some_ipv6")
    some_uri: Optional[str] = Field(default=None, alias="some_uri")
    some_uri_reference: Optional[str] = Field(default=None, alias="some_uri_reference")
    some_uri_template: Optional[str] = Field(default=None, alias="some_uri_template")
    some_json_pointer: Optional[str] = Field(default=None, alias="some_json_pointer")
    some_relative_json_pointer: Optional[str] = Field(default=None, alias="some_relative_json_pointer")
    some_regex: Optional[str] = Field(default=None, alias="some_regex")
    some_number: Optional[Decimal] = Field(default=None, alias="some_number")
    some_float: Optional[float] = Field(default=None, alias="some_float")
    some_double: Optional[float] = Field(default=None, alias="some_double")
    some_integer: Optional[int] = Field(default=None, alias="some_integer")
    some_int32: Optional[int] = Field(default=None, alias="some_int32")
    some_int64: Optional[int] = Field(default=None, alias="some_int64")
    some_boolean: Optional[bool] = Field(default=None, alias="some_boolean")
    some_array: Optional[List[str]] = Field(default=None, alias="some_array")
    some_object: Optional[Dict[str, Any]] = Field(default=None, alias="some_object")
    some_nested_object: Optional[Dict[str, Any]] = Field(default=None, alias="some_nested_object")
    some_array_of_objects: Optional[List[Dict[str, Any]]] = Field(default=None, alias="some_array_of_objects")
    some_nullable_field: Optional[Any] = Field(default=None, alias="some_nullable_field")

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
    )

    @classmethod
    def from_dict(cls, data: Any) -> "SerdeModel":
        return cls.model_validate(data)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(by_alias=True, exclude_none=True)


class ObjectSerializerTest(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.serializer = ObjectSerializer()

    def test_round_trip(self) -> None:
        orig = json.loads(open("test/resources/serde.json").read())
        model = self.serializer.deserialize(orig, SerdeModel)
        out_data = self.serializer.serialize(model)
        self.assertDictEqual(orig, out_data)
