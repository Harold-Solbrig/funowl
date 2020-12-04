from collections import UserList, Iterable
from copy import copy
from dataclasses import field
from typing import Type

from funowl.base.cast_function import cast


class ListWrapper(UserList):
    def __init__(self, l: Iterable, typ = None) -> None:
        super().__init__()
        self._typ = typ
        for e in l:
            self.append(e)

    def __add__(self, other):
        if not isinstance(other, ListWrapper):
            other = ListWrapper(copy(other), self._typ)
        return super().__add__(other)

    def __iadd__(self, other):
        raise AssertionError("+= operator does not preserve list type - use extend() instead")
        # self.extend(other)
        # return self

    def __setitem__(self, key, value):
        super().__setitem__(key, cast(self._typ, value))

    def append(self, item) -> None:
        v = cast(self._typ, item)
        if isinstance(v, list):
            super().extend(v)
        else:
            super().append(v)

    def extend(self, item) -> None:
        for i in item:
            self.append(i)

def empty_list_wrapper(typ: Type) -> ListWrapper:
    return field(default_factory = lambda: ListWrapper([], typ))
