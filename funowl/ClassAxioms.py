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

from funowl.Annotations import Annotation
from funowl.Axioms import Axiom
from funowl.ClassExpressions import ClassExpression, Class
from funowl.Declarations import ObjectPropertyExpression, DataPropertyExpression
from funowl.FunOwlBase import empty_list


class ClassAxiom(Axiom):
    pass


@dataclass
class SubClassOf(ClassAxiom):
    sub: ClassExpression
    super: ClassExpression
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.sub.as_owl() + ' ' + self.super.as_owl())


@dataclass
class EquivalentClasses(ClassAxiom):
    exprs: List[ClassExpression]

    def as_owl(self, indent: int = 0) -> str:
        return self.list_cardinality(self.exprs, 'exprs', 2).annots(indent, lambda i1: self.iter(i1, self.exprs))


@dataclass
class DisjointClasses(ClassAxiom):
    exprs: List[ClassExpression]

    def as_owl(self, indent: int = 0) -> str:
        return self.list_cardinality(self.exprs, 'exprs', 2).annots(indent, lambda i1: self.iter(i1, self.exprs))


@dataclass
class DisjointUnion(ClassAxiom):
    cls: Class
    exprs: List[ClassExpression]

    def as_owl(self, indent: int = 0) -> str:
        return self.list_cardinality(self.exprs, 'exprs', 2).\
            annots(indent, lambda i1: self.cls.as_owl(i1) + ' ' + self.iter(i1, self.exprs))



class HasKey(Axiom):
    classexpr: ClassExpression
    objexprs: List[ObjectPropertyExpression] = empty_list()
    propexprs: List[DataPropertyExpression] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent,
                           lambda i1: self.classexpr.as_owl() +
                           '\n' + self.i(i1+1) + '( ' + self.iter(i1+1, self.objexprs) + ' )' +
                           '\n' + self.i(i1+1) + '( ' + self.iter(i1+1, self.propexprs) + ' )')
