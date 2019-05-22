"""
Assertion :=
    SameIndividual | DifferentIndividuals | ClassAssertion |
    ObjectPropertyAssertion | NegativeObjectPropertyAssertion |
    DataPropertyAssertion | NegativeDataPropertyAssertion

sourceIndividual := Individual
targetIndividual := Individual
targetValue := Literal

SameIndividual := 'SameIndividual' '(' axiomAnnotations Individual Individual { Individual } ')'

DifferentIndividuals := 'DifferentIndividuals' '(' axiomAnnotations Individual Individual { Individual } ')'

ClassAssertion := 'ClassAssertion' '(' axiomAnnotations ClassExpression Individual ')'

ObjectPropertyAssertion := 'ObjectPropertyAssertion' '(' axiomAnnotations ObjectPropertyExpression sourceIndividual targetIndividual ')'

NegativeObjectPropertyAssertion := 'NegativeObjectPropertyAssertion' '(' axiomAnnotations ObjectPropertyExpression sourceIndividual targetIndividual ')'

DataPropertyAssertion := 'DataPropertyAssertion' '(' axiomAnnotations DataPropertyExpression sourceIndividual targetValue ')'

NegativeDataPropertyAssertion := 'NegativeDataPropertyAssertion' '(' axiomAnnotations DataPropertyExpression sourceIndividual targetValue ')' 
"""
from dataclasses import dataclass
from typing import List

from funowl.Annotations import Annotation
from funowl.Axioms import Axiom
from funowl.ClassExpressions import ClassExpression
from funowl.Declarations import ObjectPropertyExpression, DataPropertyExpression
from funowl.FunOwlBase import empty_list
from funowl.Individuals import Individual


class Assertion(Axiom):
    pass


@dataclass
class SameIndividual(Assertion):
    individuals: List[Individual]
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.list_cardinality(self.individuals, 'individuals', 2).\
            annots(indent, lambda i1: self.iter(i1, self.individuals))


@dataclass
class DifferentIndividuals(Assertion):
    individuals: List[Individual]
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.list_cardinality(self.individuals, 'individuals', 2).\
            annots(indent, lambda i1: self.iter(i1, self.individuals))


@dataclass
class ClassAssertion(Assertion):
    expr: ClassExpression
    individual: Individual
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.expr.as_owl() + ' ' + self.individual.as_owl())


@dataclass
class ObjectPropertyAssertion(Assertion):
    objexpr: ObjectPropertyExpression
    source: Individual
    target: Individual
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.objexpr.as_owl() + ' ' +
                                              self.source.as_owl() + ' ' + self.target.as_owl())


@dataclass
class NegativeObjectPropertyAssertion(Assertion):
    objexpr: ObjectPropertyExpression
    source: Individual
    target: Individual
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.objexpr.as_owl() + ' ' +
                                              self.source.as_owl() + ' ' + self.target.as_owl())


@dataclass
class DataPropertyAssertion(Assertion):
    propexpr: DataPropertyExpression
    source: Individual
    target: Individual
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.propexpr.as_owl() +
                                              ' ' + self.source.as_owl() + ' ' + self.target.as_owl())


@dataclass
class NegativeDataPropertyAssertion(Assertion):
    propexpr: DataPropertyAssertion
    source: Individual
    target: Individual
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.propexpr.as_owl() + ' ' +
                                              self.source.as_owl() + ' ' + self.target.as_owl())
