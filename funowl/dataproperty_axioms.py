from dataclasses import dataclass
from typing import List, Union

from rdflib import Graph, OWL, RDFS, RDF, BNode

from funowl.annotations import Annotation, Annotatable
from funowl.base.list_support import empty_list_wrapper, ListWrapper
from funowl.base.rdftriple import SUBJ
from funowl.class_expressions import ClassExpression
from funowl.converters.rdf_converter import SEQ
from funowl.dataproperty_expressions import DataPropertyExpression
from funowl.dataranges import DataRange
from funowl.literals import Datatype
from funowl.writers.FunctionalWriter import FunctionalWriter

"""
(Annotatable) :=
    SubDataPropertyOf | EquivalentDataProperties | DisjointDataProperties |
    DataPropertyDomain | DataPropertyRange | FunctionalDataProperty

SubDataPropertyOf := 'SubDataPropertyOf' '(' axiomAnnotations subDataPropertyExpression superDataPropertyExpression ')'
subDataPropertyExpression := DataPropertyExpression
superDataPropertyExpression := DataPropertyExpression

EquivalentDataProperties := 'EquivalentDataProperties' '(' axiomAnnotations DataPropertyExpression DataPropertyExpression { DataPropertyExpression } ')'

DisjointDataProperties := 'DisjointDataProperties' '(' axiomAnnotations DataPropertyExpression DataPropertyExpression { DataPropertyExpression } ')'

DataPropertyDomain := 'DataPropertyDomain' '(' axiomAnnotations DataPropertyExpression ClassExpression ')'

DataPropertyRange := 'DataPropertyRange' '(' axiomAnnotations DataPropertyExpression DataRange ')'

FunctionalDataProperty := 'FunctionalDataProperty' '(' axiomAnnotations DataPropertyExpression ')'

DatatypeDefinition := 'DatatypeDefinition' '(' axiomAnnotations Datatype DataRange ')'
"""


@dataclass
class SubDataPropertyOf(Annotatable):
    subDataPropertyExpression: DataPropertyExpression
    superDataPropertyExpression: DataPropertyExpression
    annotations: List[Annotation] = empty_list_wrapper(Annotation)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.subDataPropertyExpression + self.superDataPropertyExpression)

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> None:
        # T(DPE1) rdfs:subPropertyOf T(DPE2) .
        self.add_triple(g, self.subrDataPropertyExpression.to_rdf(g), RDFS.subPropertyOf,
                        self.superDataPropertyExpression.to_rdf(g))


@dataclass
class EquivalentDataProperties(Annotatable):
    dataPropertyExpressions: List[DataPropertyExpression]
    annotations: List[Annotation] = empty_list_wrapper(Annotation)

    def __init__(self, *dataPropertyExpressions: DataPropertyExpression, annotations: List[Annotation] = None) -> None:
        self.dataPropertyExpressions = list(dataPropertyExpressions)
        self.annotations = annotations or []
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.dataPropertyExpressions, 'exprs', 2)
        return self.annots(w, lambda: w.iter(self.dataPropertyExpressions))

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> None:
        # T(DPE1) owl:equivalentProperty T(DPE2) .
        # ...
        # T(DPEn-1) owl:equivalentProperty T(DPEn) .
        for t1, t2 in zip(self.dataPropertyExpressions[:-1], self.dataPropertyExpressions[1:]):
            self.add_triple(g, t1.to_rdf(g), OWL.equivalentProperty, t2.to_rdf(g))

@dataclass
class DisjointDataProperties(Annotatable):
    dataPropertyExpressions: List[DataPropertyExpression]
    annotations: List[Annotation] = empty_list_wrapper(Annotation)

    def __init__(self, *dataPropertyExpressions: DataPropertyExpression, annotations: List[Annotation] = None) -> None:
        dpes = [DataPropertyExpression(dpe) for dpe in dataPropertyExpressions]
        self.dataPropertyExpressions = ListWrapper(dpes, DataPropertyExpression)
        self.annotations = annotations or []
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.dataPropertyExpressions, 'exprs', 2)
        return self.annots(w, lambda: w.iter(self.dataPropertyExpressions))

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> None:
        # N == 2
        #   T(DPE1) owl:propertyDisjointWith T(DPE2) .
        # N > 2
        #    _:x rdf:type owl:AllDisjointProperties .
        #    _:x owl:members T(SEQ DPE1 ... DPEn) .
        if len(self.dataPropertyExpressions) <= 2:
            self.add_triple(g, self.dataPropertyExpressions[0].to_rdf(g), OWL.propertyDisjointWith,
                            self.dataPropertyExpressions[1].to_rdf(g))
        else:
            x = BNode()
            g.add((x, RDF.type, OWL.AllDisjointProperties))
            self.add_triple(g, x, OWL.members, SEQ(g, self.dataPropertyExpressions))

    def _subjects(self, g: Graph) -> List[SUBJ]:
        rval = []
        for e in self.dataPropertyExpressions:
            rval += e._subjects(g)
        return rval

@dataclass
class DataPropertyDomain(Annotatable):
    dataPropertyExpression: DataPropertyExpression
    classExpression: ClassExpression
    annotations: List[Annotation] = empty_list_wrapper(Annotation)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.dataPropertyExpression + ' ' + self.classExpression)

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> None:
        # T(DPE) rdfs:domain T(CE) .
        self.add_triple(g, self.dataPropertyExpression.to_rdf(g), RDFS.domain, self.classExpression.to_rdf(g))

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return self.dataPropertyExpression._subjects(g)

@dataclass
class DataPropertyRange(Annotatable):
    dataPropertyExpression: DataPropertyExpression
    dataRange: DataRange
    annotations: List[Annotation] = empty_list_wrapper(Annotation)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.dataPropertyExpression + ' ' + self.dataRange)

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> None:
        # T(DPE) rdfs:range T(DR) .
        return self.add_triple(g, self.dataPropertyExpression.to_rdf(g), RDFS.range, self.dataRange.to_rdf(g))

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return self.dataPropertyExpression._subjects(g)

@dataclass
class FunctionalDataProperty(Annotatable):
    dataPropertyExpression: DataPropertyExpression
    annotations: List[Annotation] = empty_list_wrapper(Annotation)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.dataPropertyExpression)

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> None:
        # T(DPE) rdf:type owl:FunctionalProperty .
        self.add_triple(g, self.dataPropertyExpression.to_rdf(g), RDF.type, OWL.FunctionalProperty)

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return self.dataPropertyExpression._subjects(g)

@dataclass
class DatatypeDefinition(Annotatable):
    datatype: Datatype
    datarange: DataRange
    annotations: List[Annotation] = empty_list_wrapper(Annotation)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.datatype + ' ' + self.datarange)

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> None:
        # T(DT) owl:equivalentClass T(DR) .
        self.add_triple(g, self.datatype.to_rdf(g), OWL.equivalentClass, self.datarange.to_rdf(g))


DataPropertyAxiom = Union[SubDataPropertyOf, EquivalentDataProperties, DisjointDataProperties, DataPropertyDomain,
                          DataPropertyRange, FunctionalDataProperty]
