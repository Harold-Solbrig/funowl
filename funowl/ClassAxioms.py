"""
ClassAxiom := SubClassOf | EquivalentClasses | DisjointClasses | DisjointUnion

SubClassOf := 'SubClassOf' '(' axiomAnnotations subClassExpression superClassExpression ')'
subClassExpression := ClassExpression
superClassExpression := ClassExpression

EquivalentClasses := 'EquivalentClasses' '(' axiomAnnotations ClassExpression ClassExpression { ClassExpression } ')'

DisjointClasses := 'DisjointClasses' '(' axiomAnnotations ClassExpression ClassExpression { ClassExpression } ')'

DisjointUnion := 'DisjointUnion' '(' axiomAnnotations Class disjointClassExpressions ')'
disjointClassExpressions := ClassExpression ClassExpression { ClassExpression }
"""
from dataclasses import dataclass
from typing import List

from funowl.base.list_support import empty_list
from funowl.writers import FunctionalWriter
from funowl.Annotations import Annotation
from funowl.Axioms import Axiom
from funowl.ClassExpressions import ClassExpression, Class
from funowl.Declarations import ObjectPropertyExpression, DataPropertyExpression


class ClassAxiom(Axiom):
    pass


@dataclass
class SubClassOf(ClassAxiom):
    subClassExpression: ClassExpression
    superClassExpression: ClassExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.subClassExpression + ' ' +  self.superClassExpression)


@dataclass
class EquivalentClasses(ClassAxiom):
    classExpressions: List[ClassExpression]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.classExpressions, 'exprs', 2)
        return self.annots(w, lambda: w.iter(self.classExpressions))


@dataclass
class DisjointClasses(ClassAxiom):
    classExpressions: List[ClassExpression]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.classExpressions, 'exprs', 2)
        return self.annots(w, lambda: w.iter(self.classExpressions))


@dataclass
class DisjointUnion(ClassAxiom):
    cls: Class
    disjointClassExpressions: List[ClassExpression]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.disjointClassExpressions, 'exprs', 2)
        return self.annots(w, lambda: (w + self.cls).iter(self.classExpressions))


class HasKey(Axiom):
    classExpression: ClassExpression
    objectPropertyExpressions: List[ObjectPropertyExpression] = empty_list()
    dataPropertyExpressions: List[DataPropertyExpression] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: (w + self.classExpression + '(').iter(self.objectPropertyExpressions) + ')')
