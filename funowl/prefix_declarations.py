from dataclasses import dataclass
from typing import Optional, List

from rdflib import Graph
from rdflib.namespace import NamespaceManager, OWL
from rdflib.term import Node, URIRef

from funowl.base.fun_owl_base import FunOwlBase, FunOwlRoot
from funowl.writers.FunctionalWriter import FunctionalWriter
from funowl.general_definitions import PrefixName, FullIRI


@dataclass
class Prefix(FunOwlBase):
    prefixName: Optional[PrefixName]
    fullIRI: FullIRI

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w.concat((self.prefixName or '') + ':', '=',
                                             URIRef(str(self.fullIRI)).n3(), sep=' '))

    def to_rdf(self, g: Graph) -> Optional[Node]:
        """
        Add the prefix binding to the graph
        :param g: Graph to add binding to
        :return: None -- no corresponding node
        """
        g.bind(self.prefixName, self.fullIRI.as_rdf())
        return None


class PrefixDeclarations(NamespaceManager):
    def __init__(self) -> None:
        self._init = True
        super().__init__(Graph())
        self.bind('owl', OWL)
        self._init = False

    def pdlist(self) -> List[Prefix]:
        return [Prefix(ns if ns else None, uri) for (ns, uri) in self.namespaces()]

    def __setattr__(self, key, value):
        if key.startswith('_') or self._init or key in self.__dict__:
            super().__setattr__(key, value)
        else:
            self.append(Prefix(key, value))

    def add(self, decls: List[Prefix]) -> None:
        for decl in decls:
            self.append(decl)

    def append(self, decl: Prefix) -> None:
        self.bind(decl.prefixName, decl.fullIRI)

    def bind(self, prefix, namespace, override=True, replace=True):
        """ Bind with override and replace defaults changed """
        super().bind(prefix, namespace, override, replace)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.iter(self.pdlist(), indent=False)


