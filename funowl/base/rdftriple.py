"""
Definition of RDF Subject, Predicate, Target(object) and triple
"""
from typing import Union, Tuple
from rdflib import BNode, URIRef, Literal

SUBJ = Union[BNode, URIRef]
PRED = URIRef
TARG = Union[SUBJ, Literal]

TRIPLE = Tuple[SUBJ, PRED, TARG]