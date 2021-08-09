from dataclasses import dataclass
from typing import Union

from rdflib import OWL, Graph
from rdflib.term import Node, BNode

from funowl.base.cast_function import exclude
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.identifiers import IRI
from funowl.writers import FunctionalWriter


@dataclass
class ObjectProperty(IRI):
    rdf_type = OWL.ObjectProperty


@dataclass
class ObjectInverseOf(FunOwlChoice):
    v: Union[ObjectProperty, str] = exclude([str])

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.v)

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> Node:
        x = BNode()
        assert isinstance(self.v, ObjectProperty)
        g.add((x, OWL.inverseOf, self.v.to_rdf(g)))
        return x


@dataclass
class ObjectPropertyExpression(FunOwlChoice):
    # The order below is important
    v: Union[ObjectProperty, ObjectInverseOf, str] = exclude([str])
