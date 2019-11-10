from dataclasses import dataclass
from typing import Optional, List, Union

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

    def to_rdf(self, g: Graph) -> None:
        """
        Add the prefix binding to the graph
        :param g: Graph to add binding to
        :return: None -- no corresponding node
        """
        g.bind(self.prefixName, self.fullIRI.to_rdf(g))
        return None


# TODO: there are parts of this class that are not necessary  -- in particular, it is questionable whether
#       we really need a graph to back it up
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

    def add(self, decls: Union["PrefixDeclarations", List[Prefix]]) -> None:
        """ Add an existing list of prefixes or prefix declarations  """
        for decl in decls.as_prefixes() if isinstance(decls, PrefixDeclarations) else decls:
            self.append(decl)

    def add_to_graph(self, g: Graph) -> None:
        for prefix in self.as_prefixes():
            g.namespace_manager.bind(str(prefix.prefixName), str(prefix.fullIRI), True, True)

    def append(self, decl: Prefix) -> None:
        self.bind(decl.prefixName, decl.fullIRI)

    def bind(self, prefix, namespace, override=True, replace=True):
        """ Bind with override and replace defaults changed """
        super().bind(str(prefix) if prefix is not None else None, str(namespace), override, replace)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.iter(self.as_prefixes(), indent=False)


