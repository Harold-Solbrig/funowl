"""
DataRange :=
    Datatype |
    DataIntersectionOf |
    DataUnionOf |
    DataComplementOf |
    DataOneOf |
    DatatypeRestriction

DataIntersectionOf := 'DataIntersectionOf' '(' DataRange DataRange { DataRange } ')'

DataUnionOf := 'DataUnionOf' '(' DataRange DataRange { DataRange } ')'

DataComplementOf := 'DataComplementOf' '(' DataRange ')'

DataOneOf := 'DataOneOf' '(' Literal { Literal } ')'

DatatypeRestriction := 'DatatypeRestriction' '(' Datatype constrainingFacet restrictionValue { constrainingFacet restrictionValue } ')'
constrainingFacet := IRI
restrictionValue := Literal
"""
from dataclasses import dataclass
from typing import Union, List

from funowl.annotations import Annotation
from funowl.identifiers import IRI
from funowl.literals import Datatype
from funowl.literals import Literal
from funowl.base.fun_owl_base import FunOwlBase
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.writers.FunctionalWriter import FunctionalWriter


@dataclass
class DataIntersectionOf(FunOwlBase):
    dataRanges: List["DataRange"]

    def __init__(self, *dataRanges: List["DataRange"]) -> None:
        self.dataRanges = list(dataRanges)
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.dataRanges, 'dataRange', 2)
        return w.func(self, lambda: w.iter(self.dataRanges))


@dataclass
class DataUnionOf(FunOwlBase):
    dataRanges: List["DataRange"]

    def __init__(self, *dataRanges: List["DataRange"]) -> None:
        self.dataRanges = list(dataRanges)
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.dataRanges, 'dataRange', 2)
        return w.func(self, lambda: w.iter(self.dataRanges))


@dataclass
class DataComplementOf(FunOwlBase):
    dataRange: "DataRange"

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.dataRange)

@dataclass
class DataOneOf(FunOwlBase):
    literal: List[Literal]

    def __init__(self, *literal: List[Literal]) -> None:
        self.literal = list(literal)
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w.iter(self.literal))


@dataclass
class FacetRestriction(FunOwlBase):
    constrainingFacet: IRI
    restrictionValue: Literal

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w + self.constrainingFacet + self.restrictionValue


@dataclass
class DatatypeRestriction(FunOwlBase):
    datatype: Datatype
    restrictions: List[FacetRestriction]

    def __init__(self, datatype: Datatype, *restrictions: FacetRestriction, annotations: List[Annotation] = None) \
            -> None:
        self.datatype = datatype
        self.restrictions = [FacetRestriction(r[0], r[1]) for r in zip(*[restrictions[i::2] for i in range(2)])]
        self.annotations = annotations or []
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.datatype).iter(self.restrictions))


DataRange = Union[Datatype, DataIntersectionOf, DataUnionOf, DataComplementOf, DataOneOf, DatatypeRestriction]
