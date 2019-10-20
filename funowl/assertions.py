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

ObjectPropertyAssertion := 'ObjectPropertyAssertion'
                            '(' axiomAnnotations ObjectPropertyExpression sourceIndividual targetIndividual ')'

NegativeObjectPropertyAssertion := 'NegativeObjectPropertyAssertion'
                            '(' axiomAnnotations ObjectPropertyExpression sourceIndividual targetIndividual ')'

DataPropertyAssertion := 'DataPropertyAssertion'
                            '(' axiomAnnotations DataPropertyExpression sourceIndividual targetValue ')'

NegativeDataPropertyAssertion := 'NegativeDataPropertyAssertion'
                            '(' axiomAnnotations DataPropertyExpression sourceIndividual targetValue ')'
"""
from dataclasses import dataclass
from typing import List, Optional

from rdflib import Graph, OWL
from rdflib.term import Node

from funowl.converters.rdf_converter import SEQ
from funowl.dataproperty_expressions import DataPropertyExpression
from funowl.objectproperty_expressions import ObjectPropertyExpression
from funowl.base.list_support import empty_list
from funowl.writers import FunctionalWriter
from funowl.annotations import Annotation
from funowl.axioms import Axiom
from funowl.class_expressions import ClassExpression
from funowl.individuals import Individual
from funowl.literals import Literal


@dataclass
class Assertion(Axiom):
    pass


@dataclass(init=False)
class SameIndividual(Assertion):
    individuals: List[Individual]
    annotations: List[Annotation] = empty_list()

    def __init__(self, *individuals: Individual, annotations: Optional[List[Annotation]] = None) -> None:
        self.individuals = list(individuals)
        self.annotations = annotations if annotations else []

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.list_cardinality(self.individuals, 'individuals', 2).\
            annots(w, lambda: w.iter(self.individuals, f=lambda o: w + o, indent=False))

    def to_rdf(self, g: Graph) -> Optional[Node]:
        for annotation in self.annotations:
            annotation.to_rdf(g)
        for i in range(1, len(self.individuals)):
            g.add( (self.individuals[i-1].to_rdf(g), OWL.sameAs, self.individuals[i].to_rdf(g)))
        return None


@dataclass(init=False)
class DifferentIndividuals(Assertion):
    individuals: List[Individual]
    annotations: List[Annotation] = empty_list()

    def __init__(self, *individuals: Individual,  annotations: Optional[List[Annotation]] = None) -> None:
        self.individuals = list(individuals)
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
