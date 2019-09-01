"""
Helper functions for typing library.  Variation on the version in pyjsg library
"""
import sys
from typing import Union, Any, Iterable

if sys.version_info < (3, 8):
    def get_origin(typ):
        return getattr(typ, '__origin__', None)

    def get_args(typ):
        return getattr(typ, '__args__', None)
else:
    from typing import get_origin, get_args, Union


def is_union(etype) -> bool:
    """ Determine whether etype is a Union """
    return get_origin(etype) is Union


def is_dict(etype) -> bool:
    """ Determine whether etype is a Dict """
    return get_origin(etype) is dict


def is_iterable(etype) -> bool:
    """ Determine whether etype is a List or other iterable """
    origin = get_origin(etype)
    return origin is not None and issubclass(get_origin(etype), Iterable)


def isinstance_(x, A_tuple):
    """ native isinstance_ with the test for typing.Union overridden """
    if A_tuple is Any:
        return True
    if is_union(A_tuple):
        return any(isinstance_(x, t) for t in get_args(A_tuple))
    orig = get_origin(A_tuple)
    if orig is not None:
        return isinstance_(x, orig)
    else:
        return isinstance(x, A_tuple)
