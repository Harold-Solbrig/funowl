import logging
from dataclasses import dataclass
from typing import Any, ClassVar, get_type_hints, List, Type, Tuple, Optional

from rdflib import Graph
from rdflib.term import Node

from funowl.base.fun_owl_base import FunOwlBase
from funowl.base.cast_function import cast
from funowl.base.rdftriple import NODE
from funowl.terminals.TypingHelper import get_args, isinstance_, is_union
from funowl.writers.FunctionalWriter import FunctionalWriter


@dataclass(unsafe_hash=True)
class FunOwlChoice(FunOwlBase):
    """
    Base class for different type choices.
    - v: The actual value.  Subclasses override the possible types of v
    - _coercion_allowed: False means don't try to coerce incoming values to types -- must match exactly.
      True means try to make it fit
    """
    v: Any
    _coercion_allowed: ClassVar[bool] = True       # False means type has to be exact coming in
    input_type: ClassVar[Type] = None              # Type hint for IDE's.  Not actually included in coerrcion

    @classmethod
    def types(cls) -> List[Type]:
        """
        Return the allowed types for value v
        """
        return get_type_hints(cls)['v']

    @classmethod
    def hints(cls) -> List[Type]:
        """
        Return the allowed types for value v, removing the input_type hint
        """
        hints = cls.types()
        t = list(get_args(hints)) if is_union(hints) else [hints]
        if cls.input_type:
            t.remove(cls.input_type)
        return t

    def set_v(self, value: Any) -> bool:
        """ Default setter -- can be invoked from more elaborate coercion routines
        :param value: value to set
        :return: True if v was set
        """
        for choice_type in self.hints():
            if issubclass(type(value), choice_type) or (self._coercion_allowed and isinstance_(value, choice_type)):
                super().__setattr__('v', value)
                logging.debug(f"{type(self).__name__}: value = {str(self.v)} (type: {type(self.v).__name__})")
                return True
        return False

    def __setattr__(self, key, value):
        if key != 'v' or not self.set_v(value):
            hints = get_type_hints(type(self))
            super().__setattr__(key, cast(hints[key], value) if key in hints else value)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        """ Emit functional syntax for value

        :param w: FunctionalWriter instance
        :return: FunctionalWriter instance
        """
        return w + self.v

    def to_rdf(self, g: Graph) -> Optional[NODE]:
        """
        Add value of self to graph g and return the node (if any) that represents the element
        :param g: Target graph
        :return Node that represents graph entry, if appropriate
        """
        return self.v.to_rdf(g)

    def _is_valid(cls: Type["FunOwlChoice"], v: Any) -> bool:
        """
        Determine whether v is a valid instance of v
        :param v: value to test
        """
        for choice_type in cls.hints():
            if issubclass(type(v), choice_type):
                return True
            elif cls._coercion_allowed and isinstance(v, choice_type):
                return True
        return False

    def __str__(self) -> str:
        return str(self.v)
