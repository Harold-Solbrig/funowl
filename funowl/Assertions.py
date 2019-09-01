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
from typing import List, Optional

from funowl.base.list_support import empty_list
from funowl.writers import FunctionalWriter
from funowl.Annotations import Annotation
from funowl.Axioms import Axiom
from funowl.ClassExpressions import ClassExpression
from funowl.Declarations import ObjectPropertyExpression, DataPropertyExpression
from funowl.Individuals import Individual
from funowl.Literals import Literal


@dataclass
class Assertion(Axiom):
    pass


@dataclass(init=False)
class SameIndividual(Assertion):
    individuals: List[Individual]
    annotations: List[Annotation] = empty_list()

    def __init__(self, *individuals: Individual, annotations: Optional[List[Annotation]] = None ) -> None:
        self.individuals = individuals
        self.annotations = annotations

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.list_cardinality(self.individuals, 'individuals', 2).\
            annots(w, lambda: w.iter(self.individuals, f=lambda o: w + o, indent=False))


@dataclass(init=False)
class DifferentIndividuals(Assertion):
    individuals: List[Individual]
    annotations: List[Annotation] = empty_list()

    def __init__(self, *individuals: Individual,  annotations: Optional[List[Annotation]] = None ) -> None:
        self.individuals = individuals
        self.annotations = annotations

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.list_cardinality(self.individuals, 'individuals', 2).\
            annots(w, lambda: w.iter(self.individuals, f=lambda o: w + o, indent=False))


@dataclass
class ClassAssertion(Assertion):
    expr: ClassExpression
    individual: Individual
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.expr + self.individual)


@dataclass
class ObjectPropertyAssertion(Assertion):
    expr: ObjectPropertyExpression
    sourceIndividual: Individual
    targetIndividual: Individual
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.expr + self.sourceIndividual + self.targetIndividual)


@dataclass
class NegativeObjectPropertyAssertion(Assertion):
    expr: ObjectPropertyExpression
    sourceIndividual: Individual
    targetIndividual: Individual
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.expr + self.sourceIndividual + self.targetIndividual)


@dataclass
class DataPropertyAssertion(Assertion):
    expr: DataPropertyExpression
    sourceIndividual: Individual
    targetValue: Literal
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.expr + self.sourceIndividual + self.targetValue)


@dataclass
class NegativeDataPropertyAssertion(Assertion):
    expr: DataPropertyExpression
    sourceIndividual: Individual
    targetValue: Literal
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.expr + self.sourceIndividual + self.targetValue)
