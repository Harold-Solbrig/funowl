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

from rdflib import Graph, BNode, RDF, RDFS, OWL

from funowl.annotations import Annotation
from funowl.base.fun_owl_base import FunOwlBase
from funowl.converters.rdf_converter import SEQ
from funowl.identifiers import IRI
from funowl.literals import Datatype
from funowl.literals import Literal
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

    def to_rdf(self, g: Graph) -> BNode:
        rval = BNode()
        g.add((rval, RDF.type, RDFS.Datatype))
        g.add((rval, OWL.intersectionOf, SEQ(g, self.dataRanges)))
        return rval

@dataclass
class DataUnionOf(FunOwlBase):
    dataRanges: List["DataRange"]

    def __init__(self, *dataRanges: List["DataRange"]) -> None:
        self.dataRanges = list(dataRanges)
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.dataRanges, 'dataRange', 2)
        return w.func(self, lambda: w.iter(self.dataRanges))

    def to_rdf(self, g: Graph) -> BNode:
        rval = BNode()
        g.add((rval, RDF.type, RDFS.Datatype))
        g.add((rval, OWL.intersectionOf, SEQ(g, self.dataRanges)))
        return rval


@dataclass
class DataComplementOf(FunOwlBase):
    dataRange: "DataRange"

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.dataRange)

    def to_rdf(self, g: Graph) -> BNode:
        rval = BNode()
        g.add((rval, RDF.type, RDFS.Datatype))
        g.add((rval, OWL.datatypeComplementOf, self.dataRange.to_rdf(g)))
        return rval

@dataclass
class DataOneOf(FunOwlBase):
    literal: List[Literal]

    def __init__(self, *literal: List[Literal]) -> None:
        self.literal = list(literal)
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w.iter(self.literal))

    def to_rdf(self, g: Graph) -> BNode:
        rval = BNode()
        g.add((rval, RDF.type, RDFS.Datatype))
        g.add((rval, OWL.oneOf, SEQ(self.literal)))
        return rval


@dataclass
class FacetRestriction(FunOwlBase):
    constrainingFacet: IRI
    restrictionValue: Literal

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w + self.constrainingFacet + self.restrictionValue

    def to_rdf(self, g: Graph) -> BNode:
        rval = BNode()
        g.add((rval, self.constrainingFacet.to_rdf(g), self.restrictionValue.to_rdf(g)))
        return rval


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

    def to_rdf(self, g: Graph) -> BNode:
        rval = BNode()
        g.add((rval, RDF.type, RDFS.Datatype))
        g.add((rval, OWL.onDatatype, self.datatype.to_rdf(g)))
        g.add((rval, OWL.withRestrictions, SEQ([restriction.to_rdf(g) for restriction in self.restrictions])))
        return rval


DataRange = Union[Datatype, DataIntersectionOf, DataUnionOf, DataComplementOf, DataOneOf, DatatypeRestriction]
