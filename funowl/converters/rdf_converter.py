from typing import Optional, List

from rdflib import Graph, RDF
from rdflib.collection import Collection
from rdflib.term import Node, BNode

from funowl.base.fun_owl_base import FunOwlRoot


def SEQ(g: Graph, members: List[FunOwlRoot]) -> BNode:
    if not members:
        return RDF.nil
    subj = BNode()
    Collection(g, subj, [m.to_rdf(g) for m in members])
    return subj
