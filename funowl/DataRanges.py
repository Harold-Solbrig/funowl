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

from funowl.Declarations import Datatype
from funowl.FunOwlBase import FunOwlChoice, FunOwlBase
from funowl.Identifiers import IRI
from funowl.Literals import Literal


@dataclass
class DataRange(FunOwlChoice):
    v : Union[Datatype, "DataRange_"]


class DataRange_(FunOwlBase):
    pass


@dataclass
class DataIntersectionOf(DataRange_):
    elements: List[DataRange]

    def as_owl(self, indent: int = 0) -> str:
        self.list_cardinality(self.elements, 'elements', 2)
        self.func_name(indent, lambda i1: self.iter(i1, self.elements))


@dataclass
class DataUnionOf(DataRange_):
    elements: List[DataRange]

    def as_owl(self, indent: int = 0) -> str:
        self.list_cardinality(self.elements, 'elements', 2)
        self.func_name(indent, lambda i1: self.iter(i1, self.elements))


@dataclass
class DataComplementOf(DataRange_):
    element: DataRange

    def as_owl(self, indent: int = 0) -> str:
        self.func_name(indent, lambda i1: self.element.as_owl())


@dataclass
class FacetRestriction(FunOwlBase):
    constrainingFacet: IRI
    restrictionValue: Literal

    def as_owl(self, indent: int = 0) -> str:
        return self.i(indent) + self.constrainingFacet.as_owl() + ' ' + self.restrictionValue.as_owl()


@dataclass
class DatatypeRestriction(DataRange_):
    datatype: Datatype
    restrictions: List[FacetRestriction]

    def as_owl(self, indent: int = 0) -> str:
        self.list_cardinality(self.restrictions, 'restrictions', 1)
        self.func_name(indent, lambda i1: self.datatype.as_owl() + '\n' + self.iter(i1, self.restrictions))
