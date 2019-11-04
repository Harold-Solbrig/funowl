from collections import UserList
from copy import copy
from dataclasses import field

from funowl.base.cast_function import cast


def empty_list():
    """ Shortcut dataclass list factory initializer """
    return field(default_factory=list)


class ListWrapper(UserList):
    def __init__(self, l, typ = None) -> None:
        super().__init__()
        self._typ = typ
        self.data = l

    def __add__(self, other):
        if not isinstance(other, ListWrapper):
            other = ListWrapper(copy(other), self._typ)
            other._typ = self._typ
        super().__add__(other)

    def __setitem__(self, key, value):
        super().__setitem__(key, cast(self._typ, value))

    def append(self, item) -> None:
        v = cast(self._typ, item)
        if isinstance(v, list):
            super().extend(v)
        else:
            super().append(v)
