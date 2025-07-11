import datetime
import decimal
from enum import Enum
from typing import Any, Protocol, Type, TypeVar, no_type_check

from pydantic import SecretStr

# noinspection PyPep8Naming

T = TypeVar("T", bound="Deserializable")

class Deserializable(Protocol):
    """A protocol for objects that can be created from a dictionary."""
    @classmethod
    def from_dict(cls: Type[T], data: Any) -> T:
        ...

class ObjectSerializer:
    @staticmethod
    @no_type_check
    def sanitize_for_serialization(self, obj: Any) -> Any:
        """Builds a JSON POST object.

        If obj is None, return None.
        If obj is SecretStr, return obj.get_secret_value()
        If obj is str, int, long, float, bool, return directly.
        If obj is datetime.datetime, datetime.date
            convert to string in iso8601 format.
        If obj is decimal.Decimal return string representation.
        If obj is list, sanitize each element in the list.
        If obj is dict, return the dict.
        If obj is OpenAPI model, return the properties' dict.

        :param self:
        :param obj: The data to serialize.
        :return: The serialized form of data.
        """
        if obj is None:
            return None
        elif isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, SecretStr):
            return obj.get_secret_value()
        elif isinstance(obj, self.PRIMITIVE_TYPES):
            return obj
        elif isinstance(obj, list):
            return [self.sanitize_for_serialization(sub_obj) for sub_obj in obj]
        elif isinstance(obj, tuple):
            return tuple(self.sanitize_for_serialization(sub_obj) for sub_obj in obj)
        elif isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return str(obj)

        elif isinstance(obj, dict):
            obj_dict = obj
        else:
            # Convert model obj to dict except
            # attributes `openapi_types`, `attribute_map`
            # and attributes which value is not None.
            # Convert attribute name to json key in
            # model definition for request.
            if hasattr(obj, "to_dict") and callable(obj.to_dict):
                obj_dict = obj.to_dict()
            else:
                obj_dict = obj.__dict__

        return {key: self.sanitize_for_serialization(val) for key, val in obj_dict.items()}

    @staticmethod
    def deserialize(data: Any, cls: Type[T]) -> T:
        """
        data: parsed JSON or raw
        cls: a real class implementing Deserializable
        returns: an instance of cls
        """
        # now mypy knows cls is Type[T], with T bound to Deserializable
        return cls.from_dict(data)
