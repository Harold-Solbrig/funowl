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
from typing import List, Any, Optional

from funowl.DatapropertyExpressions import DataPropertyExpression
from funowl.ObjectpropertyExpressions import ObjectPropertyExpression
from funowl.base.list_support import empty_list
from funowl.writers import FunctionalWriter
from funowl.Annotations import Annotation
from funowl.Axioms import Axiom
from funowl.ClassExpressions import ClassExpression, Class


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
    annotations: List[Annotation] = empty_list()

    def __init__(self, *classExpression: ClassExpression, annotations: List[Annotation] = None) -> None:
        self.classExpressions = list(classExpression)
        self.annotations = annotations or []

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.classExpressions, 'classExpressions', 2)
        return self.annots(w, lambda: w.iter(self.classExpressions))


@dataclass
class DisjointClasses(ClassAxiom):
    classExpressions: List[ClassExpression]
    annotations: List[Annotation] = empty_list()

    def __init__(self, *classExpression: ClassExpression, annotations: List[Annotation] = None) -> None:
        self.classExpressions = list(classExpression)
        self.annotations = annotations or []
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.classExpressions, 'classExpressions', 2)
        return self.annots(w, lambda: w.iter(self.classExpressions))


@dataclass
class DisjointUnion(ClassAxiom):
    cls: Class
    disjointClassExpressions: List[ClassExpression]
    annotations: List[Annotation] = empty_list()

    def __init__(self, cls: Class, *disjointClassExpression: ClassExpression,
                 annotations: List[Annotation] = None) -> None:
        self.cls = cls
        self.disjointClassExpressions = list(disjointClassExpression)
        self.annotations = annotations or []
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.disjointClassExpressions, 'disjointClassExpressions', 3)
        return self.annots(w, lambda: (w + self.cls).iter(self.disjointClassExpressions))


@dataclass
class HasKey(Axiom):
    classExpression: ClassExpression
    objectPropertyExpressions: Optional[List[ObjectPropertyExpression]] = empty_list()
    dataPropertyExpressions: Optional[List[DataPropertyExpression]] = empty_list()
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w,
                           lambda: ((w + self.classExpression +
                                    '(').iter(self.objectPropertyExpressions) + ')' +
                                    '(').iter(self.dataPropertyExpressions))
