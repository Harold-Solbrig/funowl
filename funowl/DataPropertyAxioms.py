from abc import ABC
from dataclasses import dataclass
from typing import List

from funowl.Annotations import Annotation
from funowl.Axioms import Axiom
from funowl.ClassExpressions import ClassExpression
from funowl.DataRanges import DataRange
from funowl.Declarations import DataPropertyExpression
from funowl.FunOwlBase import FunOwlBase, empty_list
from funowl.Literals import DataType

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


class DataPropertyAxiom(Axiom):
    pass


@dataclass
class SubDataPropertyOf(DataPropertyAxiom):
    sub: DataPropertyExpression
    super: DataPropertyExpression
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent,
                           lambda i1: self.sub.as_owl() + ' ' + self.super.as_owl())


@dataclass
class EquivalentDataProperties(DataPropertyAxiom):
    exprs: List[DataPropertyExpression]
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.list_cardinality(self.exprs, 'exprs', 2).annots(indent, lambda i1: self.iter(i1, self.exprs))


@dataclass
class DisjointDataProperties(DataPropertyAxiom):
    exprs: List[DataPropertyExpression]
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.list_cardinality(self.exprs, 'exprs', 2).annots(indent, lambda i1: self.iter(i1, self.exprs))


@dataclass
class DataPropertyDomain(DataPropertyAxiom):
    prop_expr: DataPropertyExpression
    class_expr: ClassExpression
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.prop_expr.as_owl() + ' ' + self.class_expr.as_owl())


@dataclass
class DataPropertyRange(DataPropertyAxiom):
    prop_expr: DataPropertyExpression
    class_expr: ClassExpression
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.prop_expr.as_owl() + ' ' + self.class_expr.as_owl())


@dataclass
class FunctionalDataProperty(DataPropertyAxiom):
    expr: DataPropertyExpression
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.expr.as_owl())



@dataclass
class DataTypeDefinition(DataPropertyAxiom):
    datatype: DataType
    datarange: DataRange
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.datatype.as_owl() + ' ' + self.datarange.as_owl())
