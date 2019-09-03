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

from funowl.annotations import Annotation
from funowl.axioms import Axiom
from funowl.class_expressions import ClassExpression
from funowl.declarations import ObjectPropertyExpression
from funowl.base.fun_owl_base import FunOwlBase, FunOwlChoice, empty_list
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
    v: Union[ObjectPropertyExpression, ObjectPropertyChain]


@dataclass
class SubObjectPropertyOf(ObjectPropertyAxiom):
    subObjectPropertyExpression: SubObjectPropertyExpression
    superObjectPropertyExpression: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: (w + self.subObjectPropertyExpression + self.superObjectPropertyExpression))


@dataclass
class EquivalentObjectProperties(ObjectPropertyAxiom):
    objectPropertyExpressions: List[ObjectPropertyExpression]
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w.iter(self.objectPropertyExpressions))


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

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.objectPropertyExpressions, 'expressions', 2, 2)
        return w.func(self, lambda: w.iter(self.objectPropertyExpressions))

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
