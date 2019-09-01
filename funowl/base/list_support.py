from collections import UserList
from dataclasses import field

from funowl.base.cast_function import cast


def empty_list():
    """ Shortcut dataclass list factory initializer """
    return field(default_factory=list)


class ListWrapper(UserList):
    def __init__(self, l, typ) -> None:
        super().__init__()
        self._typ = typ
        self.data = l

    def __setitem__(self, key, value):
        super().__setitem__(key, cast(self._typ, value))

    def append(self, item) -> None:
        super().append(cast(self._typ, item))
