import datetime
import decimal
from enum import Enum
from typing import Any, Optional, Protocol, Type, TypeVar, Union, no_type_check

from dateutil.parser import parse
from pydantic import SecretStr

# noinspection PyPep8Naming

T = TypeVar("T", bound="Deserializable")
E = TypeVar("E", bound=Enum)
P = TypeVar("P", int, float, bool, str)


class Deserializable(Protocol):
    """A protocol for objects that can be created from a dictionary."""

    @classmethod
    def from_dict(cls: Type[T], data: Any) -> T: ...


class ObjectSerializer:
    """
    A utility class to handle serialization and deserialization of API models.
    It converts model objects to hashes and JSON strings back to typed objects.
    """

    PRIMITIVE_TYPES = (float, bool, bytes, str, int)
    NATIVE_TYPES_MAPPING = {
        "int": int,
        "long": int,
        "float": float,
        "str": str,
        "bool": bool,
        "date": datetime.date,
        "datetime": datetime.datetime,
        "decimal": decimal.Decimal,
        "object": object,
    }

    def serialize(self, obj: Any) -> Any:  # noqa C901
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
            return [self.serialize(sub_obj) for sub_obj in obj]
        elif isinstance(obj, tuple):
            return tuple(self.serialize(sub_obj) for sub_obj in obj)
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

        return {key: self.serialize(val) for key, val in obj_dict.items()}

    # noinspection PyMethodMayBeStatic
    def deserialize(self, data: Any, cls: Type[T]) -> T:
        """
        data: parsed JSON or raw
        cls: a real class implementing Deserializable
        returns: an instance of cls
        """
        return cls.from_dict(data)

    # noinspection PyTypeChecker
    @no_type_check
    def __deserialize(
        self,
        data: Any,
        klass: Type[T],
    ) -> Optional[T]:
        """
        Deserializes JSON-style data into an instance of `klass`.

        :param data: the JSON-decoded payload (None, dict, list, or primitive)
        :param klass: the actual target class (primitive, date, enum, or a model
                      with a `from_dict` method)
        :return: an instance of `klass`, or `None` if `data is None`
        """
        if data is None:
            return None

        if klass in self.PRIMITIVE_TYPES:
            return self.__deserialize_primitive(data, klass)

        if klass is object:
            return self.__deserialize_object(data)

        if klass is datetime.date:
            return self.__deserialize_date(data)
        if klass is datetime.datetime:
            return self.__deserialize_datetime(data)

        if klass is decimal.Decimal:
            return decimal.Decimal(data)

        if issubclass(klass, Enum):
            return self.__deserialize_enum(data, klass)

        return self.__deserialize_model(data, klass)

    # noinspection PyMethodMayBeStatic
    def __deserialize_object(self, value: T) -> T:
        """
        Returns the original value unchanged.

        :param value: any value to return.
        :return: the same value passed in.
        """
        return value

    # noinspection PyMethodMayBeStatic
    def __deserialize_primitive(self, data: Any, klass: Type[P]) -> Union[P, str]:
        """
        Deserializes a primitive value into the specified primitive type.

        :param data: the value to convert (often a str).
        :param klass: the target primitive type (int, float, bool, or str).
        :return: an instance of klass, or str(data) on UnicodeEncodeError,
                 or the original data on TypeError.
        """
        try:
            return klass(data)  # now mypy knows klass is e.g. int, float, bool or str
        except UnicodeEncodeError:
            return str(data)

    # noinspection PyMethodMayBeStatic
    def __deserialize_date(self, string: str) -> datetime.date:
        """
        Deserializes an ISO8601 date string into a datetime.date.

        :param string: the date string to parse.
        :return: a date object if parsing succeeds; otherwise the original string.
        :raises RuntimeError: if the string cannot be parsed as a date.
        """
        try:
            return parse(string).date()
        except (ValueError, TypeError) as err:
            raise RuntimeError(f"Failed to parse `{string}` as date object") from err

    # noinspection PyMethodMayBeStatic
    def __deserialize_datetime(self, string: str) -> datetime.datetime:
        """
        Deserializes an ISO8601 datetime string.

        :param string: the datetime string to parse.
        :return: a datetime object if parsing succeeds, otherwise the original string.
        :raises RuntimeError: if the string cannot be parsed as ISO8601.
        """
        try:
            return parse(string)
        except ValueError as err:
            raise RuntimeError(f"Failed to parse `{string}` as datetime object") from err

    # noinspection PyMethodMayBeStatic
    def __deserialize_enum(self, data: Any, klass: Type[E]) -> E:
        """
        Deserializes a primitive value into the given Enum class.

        :param data: primitive type to convert (e.g. str or int)
        :param klass: the Enum class literal
        :return: an instance of klass
        :raises RuntimeError: if the data cannot be parsed as klass
        """
        try:
            return klass(data)
        except ValueError as err:
            raise RuntimeError(f"Failed to parse `{data}` as `{klass}`") from err

    # noinspection PyMethodMayBeStatic
    def __deserialize_model(self, data: Any, klass: Type[T]) -> T:
        """
        Deserializes a dict or list into the given model class.

        :param data: the JSON-decoded dict or list
        :param klass: the model class implementing `from_dict`
        :return: an instance of klass
        """
        return klass.from_dict(data)
