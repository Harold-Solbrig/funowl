from dataclasses import dataclass
from typing import List, Union

from funowl.annotations import Annotation, Annotatable
from funowl.base.list_support import empty_list
from funowl.class_expressions import ClassExpression
from funowl.dataproperty_expressions import DataPropertyExpression
from funowl.dataranges import DataRange
from funowl.writers.FunctionalWriter import FunctionalWriter
from funowl.literals import Datatype

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
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.subDataPropertyExpression + self.superDataPropertyExpression)


@dataclass
class EquivalentDataProperties((Annotatable)):
    dataPropertyExpressions: List[DataPropertyExpression]
    annotations: List[Annotation] = empty_list()

    def __init__(self, *dataPropertyExpressions: DataPropertyExpression, annotations: List[Annotation] = None) -> None:
        self.dataPropertyExpressions = list(dataPropertyExpressions)
        self.annotations = annotations or []
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.dataPropertyExpressions, 'exprs', 2)
        return self.annots(w, lambda: w.iter(self.dataPropertyExpressions))


@dataclass
class DisjointDataProperties((Annotatable)):
    dataPropertyExpressions: List[DataPropertyExpression]
    annotations: List[Annotation] = empty_list()

    def __init__(self, *dataPropertyExpressions: DataPropertyExpression, annotations: List[Annotation] = None) -> None:
        self.dataPropertyExpressions = list(dataPropertyExpressions)
        self.annotations = annotations or []
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.dataPropertyExpressions, 'exprs', 2)
        return self.annots(w, lambda: w.iter(self.dataPropertyExpressions))


@dataclass
class DataPropertyDomain((Annotatable)):
    dataPropertyExpression: DataPropertyExpression
    classExpression: ClassExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.dataPropertyExpression + ' ' + self.classExpression)


@dataclass
class DataPropertyRange((Annotatable)):
    dataPropertyExpression: DataPropertyExpression
    dataRange: DataRange
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.dataPropertyExpression + ' ' + self.dataRange)


@dataclass
class FunctionalDataProperty((Annotatable)):
    dataPropertyExpression: DataPropertyExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.dataPropertyExpression)


@dataclass
class DatatypeDefinition((Annotatable)):
    datatype: Datatype
    datarange: DataRange
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.datatype + ' ' + self.datarange)


DataPropertyAxiom = Union[SubDataPropertyOf, EquivalentDataProperties, DisjointDataProperties, DataPropertyDomain,
                          DataPropertyRange, FunctionalDataProperty]
