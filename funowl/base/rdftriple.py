"""
Definition of RDF Subject, Predicate, Target(object) and triple
"""
from typing import Union, Tuple
from rdflib import BNode, URIRef, Literal

NODE = Union[BNode, URIRef, URIRef]
SUBJ = Union[BNode, URIRef]
PRED = Union[URIRef]
TARG = Union[SUBJ, Literal]

TRIPLE = Tuple[SUBJ, PRED, TARG]