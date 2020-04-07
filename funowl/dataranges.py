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
# TODO: Figure out ForwardRef issue (See: class_expressions for issue focus point)
from typing import Union, List, ForwardRef

from rdflib import Graph, BNode, RDF, RDFS, OWL

from funowl.annotations import Annotation
from funowl.converters.rdf_converter import SEQ
from funowl.identifiers import IRI
from funowl.literals import Datatype
from funowl.literals import Literal
from funowl.base.fun_owl_base import FunOwlBase
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.terminals.TypingHelper import proc_forwards
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
    dataRange: ForwardRef("DataRange")

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.dataRange)

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # _:x rdf:type rdfs:Datatype .
        # _:x owl:datatypeComplementOf T(DR) .
        x = BNode()
        g.add((x, RDF.type, RDFS.Datatype))
        g.add((x, OWL.datatypeComplementOf, self.dataRange.to_rdf(g)))
        return x

@dataclass
class DataOneOf(FunOwlBase):
    literal: List[Literal]

    def __init__(self, *literal: List[Literal]) -> None:
        self.literal = list(literal)
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w.iter(self.literal))

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # _:x rdf:type rdfs:Datatype .
        # _:x owl:oneOf T(SEQ lt1 ... ltn) .
        x = BNode()
        g.add((x, RDF.type, RDFS.Datatype))
        g.add((x, OWL.oneOf, SEQ(g, self.literal)))
        return x


@dataclass
class FacetRestriction(FunOwlBase):
    constrainingFacet: IRI
    restrictionValue: Literal

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w + self.constrainingFacet + self.restrictionValue

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # _:y1 F1 lt1 .
        y = BNode()
        g.add((y, self.constrainingFacet.to_rdf(g), self.restrictionValue.to_rdf(g)))
        return y


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

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # _:x rdf:type rdfs:Datatype .
        # _:x owl:onDatatype T(DT) .
        # _:x owl:withRestrictions T(SEQ _:y1 ... _:yn) .
        # _:y1 F1 lt1 .
        # ...
        # _:yn Fn ltn .
        x = BNode()
        g.add((x, RDF.type, RDFS.Datatype))
        g.add((x, OWL.onDatatype, self.datatype.to_rdf(g)))
        g.add((x, OWL.withRestrictions, SEQ(g, self.restrictions)))
        return x


DataRange = Union[Datatype, DataIntersectionOf, DataUnionOf, DataComplementOf, DataOneOf, DatatypeRestriction]

proc_forwards(DataIntersectionOf, globals())
proc_forwards(DataUnionOf, globals())
proc_forwards(DataComplementOf, globals())