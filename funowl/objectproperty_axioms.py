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
from typing import List, Union, Optional

from funowl.annotations import Annotation
from funowl.axioms import Axiom
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.base.list_support import empty_list
from funowl.class_expressions import ClassExpression
from funowl.base.fun_owl_base import FunOwlBase
from funowl.objectproperty_expressions import ObjectPropertyExpression
from funowl.writers.FunctionalWriter import FunctionalWriter


class ObjectPropertyAxiom(Axiom):
    pass


@dataclass
class ObjectPropertyChain(FunOwlBase):
    objectPropertyExpressions: List[ObjectPropertyExpression]
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w.iter(self.objectPropertyExpressions))


@dataclass
class SubObjectPropertyExpression(FunOwlChoice):
    v: Union[ObjectPropertyExpression.types(), ObjectPropertyChain]


@dataclass
class SubObjectPropertyOf(ObjectPropertyAxiom):
    subObjectPropertyExpression: SubObjectPropertyExpression.types()
    superObjectPropertyExpression: ObjectPropertyExpression.types()
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: (w + self.subObjectPropertyExpression + self.superObjectPropertyExpression))


@dataclass
class EquivalentObjectProperties(ObjectPropertyAxiom):
    objectPropertyExpressions: List[ObjectPropertyExpression]
    annotations: List[Annotation] = empty_list()

    def __init__(self, *objectPropertyExpressions: ObjectPropertyExpression,
                 annotations: Optional[List[Annotation]] = None) -> None:
        self.objectPropertyExpressions = list(objectPropertyExpressions)
        self.annotations = annotations

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w.iter(self.objectPropertyExpressions))

    def f(self, a, b, c, d=12, e=32):
        pass

@dataclass
class DisjointObjectProperties(ObjectPropertyAxiom):
    objectPropertyExpressions: List[ObjectPropertyExpression]
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w.iter(self.objectPropertyExpressions))


@dataclass
class ObjectPropertyDomain(ObjectPropertyAxiom):
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: ClassExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.objectPropertyExpression + self.classExpression)

@dataclass
class ObjectPropertyRange(ObjectPropertyAxiom):
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: ClassExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.objectPropertyExpression + self.classExpression)


@dataclass
class InverseObjectProperties(ObjectPropertyAxiom):
    objectPropertyExpressions: List[ObjectPropertyExpression]
    annotations: List[Annotation] = empty_list()

    def __init__(self, *objectPropertyExpressions: ObjectPropertyExpression, annotations: List[Annotation] = None) \
            -> None:
        self.objectPropertyExpressions = list(objectPropertyExpressions)
        self.annotations = annotations or []

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.objectPropertyExpressions, 'expressions', 2, 2)
        return w.func(self, lambda: w + self.objectPropertyExpressions[0] + self.objectPropertyExpressions[1])

@dataclass
class FunctionalObjectProperty(ObjectPropertyAxiom):
    objectPropertyExpression: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.objectPropertyExpression)


@dataclass
class InverseFunctionalObjectProperty(ObjectPropertyAxiom):
    objectPropertyExpression: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.objectPropertyExpression)


@dataclass
class ReflexiveObjectProperty(ObjectPropertyAxiom):
    objectPropertyExpression: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.objectPropertyExpression)


@dataclass
class IrreflexiveObjectProperty(ObjectPropertyAxiom):
    objectPropertyExpression: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.objectPropertyExpression)


@dataclass
class SymmetricObjectProperty(ObjectPropertyAxiom):
    objectPropertyExpression: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.objectPropertyExpression)


@dataclass
class AsyymetricObjectProperty(ObjectPropertyAxiom):
    objectPropertyExpression: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.objectPropertyExpression)


@dataclass
class TransitiveObjectProperty(ObjectPropertyAxiom):
    objectPropertyExpression: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.objectPropertyExpression)
