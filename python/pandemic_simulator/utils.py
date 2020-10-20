# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
import abc
import dataclasses
from typing import Any, cast, Type, TypeVar, Dict

import istype

__all__ = ['required', 'abstract_class_property', 'checked_cast', 'shallow_asdict']

_T = TypeVar('_T')


def required() -> _T:
    def required_err() -> Any:
        raise ValueError('Missing required field')

    return cast(_T, dataclasses.field(default_factory=required_err))


def abstract_class_property() -> _T:
    @abc.abstractmethod  # type: ignore
    def inner() -> Any:
        raise NotImplementedError

    return cast(_T, inner)


def checked_cast(type: Type[_T], obj: Any) -> _T:
    """
    Method for executing a safe cast in python
    """
    assert istype.isinstanceof(obj, type)
    return obj  # type: ignore


def shallow_asdict(x: Any) -> Dict[str, Any]:
    assert dataclasses.is_dataclass(x)
    return {field.name: getattr(x, field.name) for field in dataclasses.fields(x)}
