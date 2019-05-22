from dataclasses import field, dataclass
from inspect import getmodule
from typing import List, Optional, Union, Any, Iterable, Type, ForwardRef, Callable

from pyjsg.jsglib import isinstance_, is_union, is_iterable


def empty_list():
    return field(default_factory=list)


class FunOwlRoot:
    """ The root object for all OWL Functional representations """

    def _cast(self, typ: Type, v: Any) -> Any:
        """ Make sure that v is an instance of typ """
        if v is None or v == []:            # Null and empty list are always allowed (a bit too permissive but...
            return v
        if isinstance(typ, ForwardRef):     # Only occurs in self references in our model
            typ = typ._evaluate(getmodule(self).__dict__, None)
        if isinstance(typ, type) and issubclass(typ, FunOwlChoice):
            typ = typ.__annotations__['v']
        try:
            if issubclass(type(v), typ):
                return v                        # Already correctly typed
        except TypeError:
            pass
        if not isinstance_(v, typ):
            raise TypeError(f"{v} (type: {type(v)} cannot be converted to {typ}")

        # Union[...]
        if is_union(typ):
            for t in typ.__args__:
                if type(v) is t:
                    return v
                elif isinstance_(v, t):
                    return self._cast(t, v)
            raise TypeError(f"Type mismatch between {v} (type: {type(v)} and {typ}")    # Shouldn't be able to get here

        # List[...]
        if is_iterable(typ):
            list_type = typ.__args__[0]
            if isinstance(list_type, ForwardRef):       # Performance -- processed above if not here
                list_type = list_type._evaluate(getmodule(self).__dict__, None)
            if isinstance(v, str) or not isinstance(v, Iterable):   # You can assign a singleton directly
                v = [v]
            return [self._cast(list_type, vi) for vi in v]

        # Vanilla typing
        return typ(v)

    def __setattr__(self, key, value):
        super().__setattr__(
            key, self._cast(self.__annotations__[key], value) if key in self.__annotations__ else value)

    def as_owl(self, indent: int = 0) -> str:
        """ Return OWL functional representation """
        return self.i(indent) + str(self)

    def func_name(self, indent: int, defn: Callable[[int], str]) -> str:
        return f"{type(self).__name__}( {defn(indent)} )"

    def list_cardinality(self, els: List["FunOwlBase"], list_name: str, min_: int = 1) -> "FunOwlBase":
        if len(els) < min_:
            raise ValueError(f"{type(self).__name__}.{list_name} must have at least two expressions")
        return self

    @staticmethod
    def owl_str(v: Optional[Any], indent: int = 0) -> str:
        """ Return the OWL string representation of v """
        return '' if v is None else v.as_owl(indent) if isinstance(v, FunOwlBase) else (FunOwlBase.i(indent) + str(v))

    @staticmethod
    def i(indent: int) -> str:
        return '\t' * indent

    def iter(self, indent: int, els: List['FunOwlBase'], lastcr: bool = True) -> str:
        """ Iterate over els """
        if els:
            return (self.i(indent) + ('\n' + self.i(indent)).join([self.owl_str(el) for el in els])) + ('\n' if lastcr else '')
        return ''

    @staticmethod
    def opt(v: Optional[Union[str, "FunOwlBase"]], sep: str = ' ') -> str:
        return '' if v is None else (sep + (v.as_owl() if isinstance(v, FunOwlRoot) else str(v)))

    def _is_valid(self, instance) -> bool:
        return issubclass(type(instance), self)


class FunOwlBaseMeta(type):
    def _is_valid(cls, instance) -> bool:
        """ Instance checking override as a class method """
        return False

    def __instancecheck__(self, instance):
        return self._is_valid(self, instance)


class FunOwlBase(FunOwlRoot, metaclass=FunOwlBaseMeta):
    pass


class FunOwlChoice(FunOwlBase):
    v: Union

    def __init__(self, value: Any) -> None:
        if not isinstance_(value, self.v):
            raise ValueError(f"Incompatible value: {value} (type: {type(value)} for {type(self.v)}")
        self.v = value

    def as_owl(self, indent: int = 0) -> str:
        return self.i(indent) + self.owl_str(self.v)

    def _is_valid(self, instance) -> bool:
        return any(isinstance(instance, vi) for vi in self.__annotations__['v'].__args__)
