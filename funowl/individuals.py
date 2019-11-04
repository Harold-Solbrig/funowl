"""
Individual := NamedIndividual | AnonymousIndividual

NamedIndividual := IRI

AnonymousIndividual := nodeID
"""
from dataclasses import dataclass
from typing import Union, ClassVar

from rdflib import OWL, URIRef, Graph
from rdflib.term import BNode

from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.general_definitions import NodeID
from funowl.identifiers import IRI


@dataclass
class NamedIndividual(IRI):
    rdf_type: ClassVar[URIRef] = OWL.NamedIndividual


class AnonymousIndividual(NodeID):
    def to_rdf(self, g: Graph) -> BNode:
        return BNode()


@dataclass
class Individual(FunOwlChoice):
    v: Union[NamedIndividual, AnonymousIndividual]
