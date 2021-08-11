from dataclasses import dataclass
from typing import Optional, List, Union

from rdflib import Graph
from rdflib.namespace import NamespaceManager, OWL
from rdflib.term import URIRef

from funowl.base.cast_function import exclude
from funowl.base.fun_owl_base import FunOwlBase
from funowl.general_definitions import PrefixName, FullIRI
from funowl.writers.FunctionalWriter import FunctionalWriter


@dataclass
class Prefix(FunOwlBase):
    prefixName: Optional[Union[PrefixName, str]]
    fullIRI: FullIRI

    def __post_init__(self):
        if self.prefixName is not None and not isinstance(self.prefixName, PrefixName):
            self.prefixName = PrefixName(self.prefixName)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w.concat((self.prefixName or '') + ':', '=',
                                             URIRef(str(self.fullIRI)).n3(), sep=' '))


class PrefixDeclarations(NamespaceManager):
    def __init__(self, g: Optional[Graph] = None) -> None:
        self._init = True
        super().__init__(g if g is not None else Graph())
        self.bind('owl', OWL)
        self._init = False

    def as_prefixes(self) -> List[Prefix]:
        """ Return the contents of the manager as a list of Prefixes """
        return [Prefix(ns if ns else None, uri) for (ns, uri) in self.namespaces()]

    def __setattr__(self, key, value):
        if key.startswith('_') or self._init or key in self.__dict__:
            super().__setattr__(key, value)
        else:
            self.append(Prefix(key, value))

    def append(self, decl: Prefix) -> None:
        self.bind(decl.prefixName, decl.fullIRI)

    def bind(self, prefix, namespace, override=True, replace=True):
        """ Bind with override and replace defaults changed """
        super().bind(str(prefix) if prefix is not None else None, str(namespace), override, replace)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.iter(self.as_prefixes(), indent=False)
