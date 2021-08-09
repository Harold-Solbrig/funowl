import logging
from dataclasses import dataclass, fields, Field
from typing import Any, ClassVar, get_type_hints, List, Type, Optional, Union

from rdflib import Graph
from rdflib.term import URIRef

from funowl.base.cast_function import cast
from funowl.base.fun_owl_base import FunOwlBase
from funowl.base.rdftriple import NODE, SUBJ
from funowl.terminals.TypingHelper import isinstance_, get_args
from funowl.writers.FunctionalWriter import FunctionalWriter


@dataclass(unsafe_hash=True)
class FunOwlChoice(FunOwlBase):
    """
    Base class for different type choices.
    - v: The actual value.  Subclasses override the possible types of v
    - _coercion_allowed: False means don't try to coerce incoming values to types -- must match exactly.
      True means try to make it fit

    """
    v: Union[Any, Any]
    _coercion_allowed: ClassVar[bool] = True             # False means type has to be exact coming in

    @classmethod
    def v_field(cls) -> Field:
        for fld in fields(cls):
            if fld.name == 'v':
                return fld
        raise TypeError(f"{cls} (hash: {hash(cls)} does not define a valid choice variable ('v')")

    @classmethod
    def types(cls) -> List[Type]:
        """
        Return the choice types
        """
        return cls.v_field().type

    @classmethod
    def real_types(cls) -> List[Type]:
        """ Return the list of possible choices with exclusions removed

        Note that this code closely parallels the cast_function remove_exclusions function.  It is separate because
        of import issues
        """
        fld = cls.v_field()
        exclusions = fld.metadata.get('exclude', [])
        return [t for t in get_args(fld.type) if t not in exclusions]

    def set_v(self, value: Any) -> bool:
        """ Default setter -- can be invoked from more elaborate coercion routines
        :param value: value to set
        :return: True if v was set
        """
        for choice_type in self.real_types():
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

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> Optional[NODE]:
        """
        Add value of self to graph g and return the node (if any) that represents the element
        :param g: Target graph
        :param emit_type_arc: True means force type arc
        :return Node that represents graph entry, if appropriate
        """
        return self.v.to_rdf(g, emit_type_arc=emit_type_arc)

    def _is_valid(cls: Type["FunOwlChoice"], v: Any) -> bool:
        """
        Determine whether v is a valid instance of v
        :param v: value to test
        """
        for choice_type in cls.real_types():
            if issubclass(type(v), choice_type):
                return True
            elif cls._coercion_allowed and isinstance(v, choice_type):
                return True
        return False

    def __str__(self) -> str:
        return str(self.v)

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return self.v._subjects(g)
