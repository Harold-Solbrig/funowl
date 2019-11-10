import logging
from abc import ABCMeta
from dataclasses import dataclass
from inspect import getmodule
from typing import List, Any, get_type_hints, Tuple, Type, Optional

from rdflib import Graph
from rdflib.term import Node, URIRef

from funowl.base.cast_function import cast
from funowl.base.list_support import ListWrapper
from funowl.terminals.TypingHelper import get_args
from funowl.writers.FunctionalWriter import FunctionalWriter


@dataclass(unsafe_hash=True)
class FunOwlRoot:
    """ The root object for all OWL functional representations """
    def __post_init__(self):
        logging.debug(f"Constructed {repr(self)}")

    def __setattr__(self, key, value):
        # Resolve Forward references before we begin the cast process
        hints = get_type_hints(type(self), getmodule(self).__dict__)
        super().__setattr__(
            key, cast(hints[key], value, getattr(self, '_coercion_allowed', None)) if key in hints else value)

    def __getattribute__(self, item):
        rval = super().__getattribute__(item)
        if not item.startswith('_') and isinstance(rval, list):
            hints = get_type_hints(type(self), getmodule(self).__dict__)
            if item in hints:
                return ListWrapper(rval, get_args(hints[item])[0])
        return rval

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        """
        Render indented image of self in functional syntax
        :param w: FunctionalWriter  to add syntax to
        :return: FunctionalWriter instance
        """
        return w + str(self)

    def to_rdf(self, g: Graph) -> URIRef:
        """ Add RDF representation of self to graph g and return node representing representation if applicable """
        return URIRef(f"http://notimplemented.org/{self.__class__.__name__}")

    def list_cardinality(self, els: List, list_name: str, min_: int = 1, max_: int = None) -> "FunOwlRoot":
        """ Validate the cardinality of a list element """
        if max_ is not None:
            if max_ == min_ and len(els) != min_:
                raise ValueError(f"{type(self).__name__}.{list_name} must have exactly {min_} values")
            if len(els) > max_:
                raise ValueError(f"{type(self).__name__}.{list_name} may have at most {max_} values")
        if len(els) < min_:
            raise ValueError(f"{type(self).__name__}.{list_name} must have at least {min_} expressions")
        return self

    def _is_valid(cls: Type, instance) -> bool:
        """ Determine whether instance is a valid type of self """

        # Note: we use issubclass because we've overloaded isinstance to return true if instance can be coerced into
        # type of self.
        return issubclass(type(instance), cls)

    @classmethod
    def _parse_input(cls, v: Any) -> Tuple[Any]:
        """ Parse v into an ordered list of arguments """
        return v,


class FunOwlBaseMeta(ABCMeta):
    """ Metaclass for FunOwlBase """
    @staticmethod
    def _is_valid(cls, instance) -> bool:
        pass

    def __instancecheck__(cls, instance):
        return cls._is_valid(cls, instance)


@dataclass
class FunOwlBase(FunOwlRoot, metaclass=FunOwlBaseMeta):
    pass
