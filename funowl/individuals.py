"""
Individual := NamedIndividual | AnonymousIndividual

NamedIndividual := IRI

AnonymousIndividual := nodeID
"""
from dataclasses import dataclass
from typing import Union, ClassVar, List

from rdflib import OWL, URIRef, Graph
from rdflib.term import BNode

from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.base.rdftriple import SUBJ
from funowl.general_definitions import NodeID
from funowl.identifiers import IRI


@dataclass
class NamedIndividual(IRI):
    rdf_type: ClassVar[URIRef] = OWL.NamedIndividual

class AnonymousIndividual(NodeID):
    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        return BNode(str(self)[2:])

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return []       # There are subjects, but they don't have identity


@dataclass
class Individual(FunOwlChoice):
    v: Union[NamedIndividual, AnonymousIndividual]
