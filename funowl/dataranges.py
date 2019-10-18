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

from funowl.identifiers import IRI
from funowl.literals import Datatype
from funowl.literals import Literal
from funowl.base.fun_owl_base import FunOwlBase
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.writers.FunctionalWriter import FunctionalWriter


# A DataRange can be a DataType or any child of DataRange_
class DataRange_(FunOwlBase):
    pass


@dataclass
class DataRange(FunOwlChoice):
    v : Union[Datatype, "DataRange_"]


@dataclass
class DataIntersectionOf(DataRange_):
    dataRanges: List[DataRange]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.dataRanges, 'dataRange', 2)
        return w.func(self, lambda: w.iter(self.dataRanges))


@dataclass
class DataUnionOf(DataRange_):
    dataRanges: List[DataRange]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.dataRanges, 'dataRange', 2)
        return w.func(self, lambda: w.iter(self.dataRanges))


@dataclass
class DataComplementOf(DataRange_):
    dataRange: DataRange

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.dataRange)

@dataclass
class DataOneOf(DataRange_):
    literal: List[Literal]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.literal, "literal", 2)
        return w.func(self, w.iter(self.literal))


@dataclass
class FacetRestriction(FunOwlBase):
    constrainingFacet: IRI
    restrictionValue: Literal

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w + self.constrainingFacet + self.restrictionValue


@dataclass
class DatatypeRestriction(DataRange_):
    datatype: Datatype
    restrictions: List[FacetRestriction]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.datatype).iter(self.restrictions))
