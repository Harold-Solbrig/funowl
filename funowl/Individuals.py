"""
Individual := NamedIndividual | AnonymousIndividual

NamedIndividual := IRI

AnonymousIndividual := nodeID
"""
from typing import Union

from funowl.FunOwlBase import FunOwlChoice
from funowl.GeneralDefinitions import NodeID
from funowl.Identifiers import IRIType


class NamedIndividual(IRIType):
    pass


class AnonymousIndividual(NodeID):
    pass


class Individual(FunOwlChoice):
    v: Union[NamedIndividual, AnonymousIndividual]
