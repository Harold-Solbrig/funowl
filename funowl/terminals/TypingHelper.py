"""
Helper functions for typing library.  Variation on the version in pyjsg library
"""
import sys
from collections import UserList
from dataclasses import fields
from typing import Any, Iterable, TypeVar, _eval_type

if sys.version_info < (3, 8):
    def get_origin(typ):
        return getattr(typ, '__origin__', None)

    def get_args(typ):
        return getattr(typ, '__args__', None)
else:
    from typing import get_origin, get_args, Union


def proc_forwards(cls, glob_ns) -> None:
    for f in fields(cls):
        f.type = _eval_type(f.type, glob_ns, glob_ns)


def is_union(etype) -> bool:
    """ Determine whether etype is a Union """
    return get_origin(etype) is Union


def is_dict(etype) -> bool:
    """ Determine whether etype is a Dict """
    return get_origin(etype) is dict or etype is dict


def is_list(etype) -> bool:
    return get_origin(etype) is list or etype is list


def is_tuple(etype) -> bool:
    return get_origin(etype) is tuple or etype is tuple


def is_set(etype) -> bool:
    return get_origin(etype) is set or etype is set


def is_iterable(etype) -> bool:
    """ Determine whether etype is a List or other iterable """
    origin = get_origin(etype)
    return issubclass(etype, Iterable) if origin is None else origin is not Union and issubclass(origin, Iterable)


def issubclass_(x, A_tuple):
    return isinstance_(type(x), A_tuple)


def isinstance_(x, test_type):
    """ native isinstance_ with the test for typing.Union overridden """
    # TODO: TypeVar instances are treated as Any for the time being
    if test_type is Any or isinstance(test_type, TypeVar):
        return True

    if is_union(test_type):
        return any(isinstance_(x, t) for t in get_args(test_type))

    if is_dict(test_type):
        if isinstance(x, dict):
            dict_args = get_args(test_type)
            return all(isinstance_(k, dict_args[0]) and isinstance_(v, dict_args[1])
                       for k, v in x.items()) if dict_args else True
        else:
            return False

    if is_list(test_type):
        if isinstance(x, list) or isinstance(x, UserList):
            list_type = get_args(test_type)
            return all(isinstance_(t, list_type[0]) for t in x) if list_type else True
        else:
            return False

    if is_tuple(test_type):
        if isinstance(x, tuple):
            tuple_args = get_args(test_type)
            return all(isinstance_(xv, tv) for xv, tv in zip(x, tuple_args)) if tuple_args else True
        else:
            return False

    if is_set(test_type):
        if isinstance(x, set):
            set_type = get_args(test_type)
            return all(isinstance_(e, set_type[0]) for e in x) if set_type else True
        else:
            return False

    return get_origin(test_type) is None and isinstance(x, test_type)
