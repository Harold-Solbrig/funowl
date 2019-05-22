"""
ObjectPropertyAxiom :=
    SubObjectPropertyOf | EquivalentObjectProperties |
    DisjointObjectProperties | InverseObjectProperties |
    ObjectPropertyDomain | ObjectPropertyRange |
    FunctionalObjectProperty | InverseFunctionalObjectProperty |
    ReflexiveObjectProperty | IrreflexiveObjectProperty |
    SymmetricObjectProperty | AsymmetricObjectProperty |
    TransitiveObjectProperty

SubObjectPropertyOf := 'SubObjectPropertyOf' '(' axiomAnnotations subObjectPropertyExpression superObjectPropertyExpression ')'
subObjectPropertyExpression := ObjectPropertyExpression | propertyExpressionChain
propertyExpressionChain := 'ObjectPropertyChain' '(' ObjectPropertyExpression ObjectPropertyExpression { ObjectPropertyExpression } ')'
superObjectPropertyExpression := ObjectPropertyExpression

EquivalentObjectProperties := 'EquivalentObjectProperties' '(' axiomAnnotations ObjectPropertyExpression ObjectPropertyExpression { ObjectPropertyExpression } ')'

DisjointObjectProperties := 'DisjointObjectProperties' '(' axiomAnnotations ObjectPropertyExpression ObjectPropertyExpression { ObjectPropertyExpression } ')'

ObjectPropertyDomain := 'ObjectPropertyDomain' '(' axiomAnnotations ObjectPropertyExpression ClassExpression ')'

ObjectPropertyRange := 'ObjectPropertyRange' '(' axiomAnnotations ObjectPropertyExpression ClassExpression ')'

InverseObjectProperties := 'InverseObjectProperties' '(' axiomAnnotations ObjectPropertyExpression ObjectPropertyExpression ')'

FunctionalObjectProperty := 'FunctionalObjectProperty' '(' axiomAnnotations ObjectPropertyExpression ')'

InverseFunctionalObjectProperty := 'InverseFunctionalObjectProperty' '(' axiomAnnotations ObjectPropertyExpression ')'

ReflexiveObjectProperty := 'ReflexiveObjectProperty' '(' axiomAnnotations ObjectPropertyExpression ')'

IrreflexiveObjectProperty := 'IrreflexiveObjectProperty' '(' axiomAnnotations ObjectPropertyExpression ')'

SymmetricObjectProperty := 'SymmetricObjectProperty' '(' axiomAnnotations ObjectPropertyExpression ')'

AsymmetricObjectProperty := 'AsymmetricObjectProperty' '(' axiomAnnotations ObjectPropertyExpression ')'

TransitiveObjectProperty := 'TransitiveObjectProperty' '(' axiomAnnotations ObjectPropertyExpression ')'
"""
from dataclasses import dataclass
from typing import List, Union

from funowl.Annotations import Annotation
from funowl.Axioms import Axiom
from funowl.ClassExpressions import ClassExpression
from funowl.Declarations import ObjectPropertyExpression
from funowl.FunOwlBase import FunOwlBase, FunOwlChoice, empty_list


class ObjectPropertyAxiom(Axiom):
    pass


@dataclass
class ObjectPropertyChain(FunOwlBase):
    exprs: List[ObjectPropertyExpression]
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.list_cardinality(self.exprs, 'exprs', 2).\
            func_name(indent, lambda i1: self.iter(i1, self.exprs))


@dataclass
class SubObjectPropertyExpression(FunOwlChoice):
    v: Union[ObjectPropertyExpression, ObjectPropertyChain]


@dataclass
class SubObjectPropertyOf(ObjectPropertyAxiom):
    sub: SubObjectPropertyExpression
    super: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.sub.as_owl(i1) + ' ' + self.super.as_owl(i1))


@dataclass
class EquivalentObjectProperties(ObjectPropertyAxiom):
    exprs: List[ObjectPropertyExpression]
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.iter(i1, self.exprs))


@dataclass
class DisjointObjectProperties(ObjectPropertyAxiom):
    exprs: List[ObjectPropertyExpression]
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.iter(i1, self.exprs))


@dataclass
class ObjectPropertyDomain(ObjectPropertyAxiom):
    propexpr: ObjectPropertyExpression
    classexpr: ClassExpression
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.propexpr.as_owl() + ' ' + self.classexpr.as_owl())


@dataclass
class ObjectPropertyRange(ObjectPropertyAxiom):
    propexpr: ObjectPropertyExpression
    classexpr: ClassExpression
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.propexpr.as_owl() + ' ' + self.classexpr.as_owl())


@dataclass
class InverseObjectProperties(ObjectPropertyAxiom):
    expr1: ObjectPropertyExpression
    expr2: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.expr1.as_owl() + ' ' + self.expr2.as_owl())


@dataclass
class FunctionalObjectProperty(ObjectPropertyAxiom):
    expr: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.expr.as_owl())


@dataclass
class InverseFunctionalObjectProperty(ObjectPropertyAxiom):
    expr: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.expr.as_owl())


@dataclass
class ReflexiveObjectProperty(ObjectPropertyAxiom):
    expr: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.expr.as_owl())


@dataclass
class IrreflexiveObjectProperty(ObjectPropertyAxiom):
    expr: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.expr.as_owl())


@dataclass
class SymmetricObjectProperty(ObjectPropertyAxiom):
    expr: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.expr.as_owl())


@dataclass
class AsyymetricObjectProperty(ObjectPropertyAxiom):
    expr: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.expr.as_owl())


@dataclass
class TransitiveObjectProperty(ObjectPropertyAxiom):
    expr: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.expr.as_owl())
