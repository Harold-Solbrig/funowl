from dataclasses import dataclass
from typing import List

from funowl.Annotations import Annotation
from funowl.Axioms import Axiom
from funowl.ClassExpressions import ClassExpression
from funowl.DataRanges import DataRange
from funowl.Declarations import DataPropertyExpression
from funowl.base.fun_owl_base import empty_list
from funowl.writers.FunctionalWriter import FunctionalWriter
from funowl.Literals import Datatype

"""
DataPropertyAxiom :=
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
class DataPropertyAxiom(Axiom):
    pass


@dataclass
class SubDataPropertyOf(DataPropertyAxiom):
    subDataPropertyExpression: DataPropertyExpression
    superDataPropertyExpression: DataPropertyExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.subDataPropertyExpression + self.superDataPropertyExpression)


@dataclass
class EquivalentDataProperties(DataPropertyAxiom):
    dataPropertyExpressions: List[DataPropertyExpression]
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.dataPropertyExpressions, 'exprs', 2)
        return self.annots(w, lambda: w.iter(self.dataPropertyExpressions))


@dataclass
class DisjointDataProperties(DataPropertyAxiom):
    dataPropertyExpressions: List[DataPropertyExpression]
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.dataPropertyExpressions, 'exprs', 2)
        return self.annots(w, lambda: w.iter(self.dataPropertyExpressions))


@dataclass
class DataPropertyDomain(DataPropertyAxiom):
    dataPropertyExpression: DataPropertyExpression
    classExpression: ClassExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.dataPropertyExpression + ' ' + self.classExpression)


@dataclass
class DataPropertyRange(DataPropertyAxiom):
    dataPropertyExpression: DataPropertyExpression
    dataRange: DataRange
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.dataPropertyExpression + ' ' + self.dataRange)


@dataclass
class FunctionalDataProperty(DataPropertyAxiom):
    dataPropertyExpression: DataPropertyExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.dataPropertyExpression)


@dataclass
class DataTypeDefinition(DataPropertyAxiom):
    datatype: Datatype
    datarange: DataRange
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.datatype + ' ' + self.datarange)
