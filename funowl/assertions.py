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
from typing import List, Optional, Union

from rdflib import Graph, OWL, RDF
from rdflib.term import BNode

from funowl.annotations import Annotation, Annotatable
from funowl.base.list_support import empty_list
from funowl.class_expressions import ClassExpression
from funowl.converters.rdf_converter import SEQ
from funowl.dataproperty_expressions import DataPropertyExpression
from funowl.individuals import Individual
from funowl.literals import Literal
from funowl.objectproperty_expressions import ObjectPropertyExpression, ObjectInverseOf
from funowl.writers import FunctionalWriter


@dataclass
class SameIndividual(Annotatable):
    individuals: List[Individual]
    annotations: List[Annotation] = empty_list()

    def __init__(self, *individuals: Individual, annotations: Optional[List[Annotation]] = None) -> None:
        self.individuals = list(individuals)
        self.annotations = annotations or []
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.list_cardinality(self.individuals, 'individuals', 2).\
            annots(w, lambda: w.iter(self.individuals, f=lambda o: w + o, indent=False))

    def to_rdf(self, g: Graph) -> None:
        for i in range(1, len(self.individuals)):
            self.add_triple(g, self.individuals[i-1].to_rdf(g), OWL.sameAs, self.individuals[i].to_rdf(g))


@dataclass
class DifferentIndividuals(Annotatable):
    individuals: List[Individual]
    annotations: List[Annotation] = empty_list()

    def __init__(self, *individuals: Individual,  annotations: Optional[List[Annotation]] = None) -> None:
        self.individuals = list(individuals)
        self.annotations = annotations or []
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.list_cardinality(self.individuals, 'individuals', 2).\
            annots(w, lambda: w.iter(self.individuals, f=lambda o: w + o, indent=False))

    def to_rdf(self, g: Graph) -> None:
        if len(self.individuals) == 2:
            self.add_triple(g, self.individuals[0].to_rdf(g), OWL.differentFrom, self.individuals[1].to_rdf(g))
        elif len(self.individuals) > 2:
            subj = BNode()
            g.add((subj, RDF.type, OWL.AllDifferent))
            g.add((subj, OWL.memebers, SEQ(g, self.individuals)))
            self.TANN(g, subj)
        return None


@dataclass
class ClassAssertion(Annotatable):
    expr: ClassExpression
    individual: Individual
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.expr + self.individual)

    def to_rdf(self, g: Graph) -> None:
        self.add_triple(g, self.individual.to_rdf(g), RDF.type, self.expr.to_rdf(g))


@dataclass
class ObjectPropertyAssertion(Annotatable):
    # Should be ObjectProperty instead of ObjectPropertyExpression
    expr: ObjectPropertyExpression
    sourceIndividual: Individual
    targetIndividual: Individual
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.expr + self.sourceIndividual + self.targetIndividual)

    def to_rdf(self, g: Graph) -> None:
        # ObjectPropertyAssertion( OP a1 a2 ) 	T(a1) T(OP) T(a2) .
        # ObjectPropertyAssertion( ObjectInverseOf( OP ) a1 a2 ) 	T(a2) T(OP) T(a1) .
        if issubclass(type(self.expr), ObjectInverseOf):
            self.add_triple(g, self.targetIndividual.to_rdf(g), self.expr.v.v.to_rdf(g),
                            self.sourceIndividual.to_rdf(g))
        else:
            self.add_triple(g, self.sourceIndividual.to_rdf(g), self.expr.to_rdf(g), self.targetIndividual.to_rdf(g))


@dataclass
class NegativeObjectPropertyAssertion(Annotatable):
    expr: ObjectPropertyExpression
    sourceIndividual: Individual
    targetIndividual: Individual
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.expr + self.sourceIndividual + self.targetIndividual)

    def to_rdf(self, g: Graph) -> None:
        subj = BNode()
        g.add((subj, RDF.type, OWL.NegativePropertyAssertion))
        g.add((subj, OWL.sourceIndividual, self.sourceIndividual.to_rdf(g)))
        g.add((subj, OWL.assertionProperty, self.expr.to_rdf(g)))
        g.add((subj, OWL.targetIndividual, self.targetIndividual.to_rdf(g)))
        self.TANN(g, subj)


@dataclass
class DataPropertyAssertion(Annotatable):
    expr: DataPropertyExpression
    sourceIndividual: Individual
    targetValue: Literal
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.expr + self.sourceIndividual + self.targetValue)

    def to_rdf(self, g: Graph) -> None:
        self.add_triple(g, self.sourceIndividual.to_rdf(g), self.expr.to_rdf(g), self.targetValue.to_rdf(g))


@dataclass
class NegativeDataPropertyAssertion(Annotatable):
    expr: DataPropertyExpression
    sourceIndividual: Individual
    targetValue: Literal
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.expr + self.sourceIndividual + self.targetValue)

    def to_rdf(self, g: Graph) -> None:
        subj = BNode()
        g.add((subj, RDF.type, OWL.NegativePropertyAssertion))
        g.add((subj, OWL.sourceIndividual, self.sourceIndividual.to_rdf(g)))
        g.add((subj, OWL.assertionProperty, self.expr.to_rdf(g)))
        g.add((subj, OWL.targetValue, self.targetValue.to_rdf(g)))
        self.TANN(g, subj)

        
Assertion = Union[SameIndividual, DifferentIndividuals, ClassAssertion, ObjectPropertyAssertion,
                  NegativeObjectPropertyAssertion, DataPropertyAssertion, NegativeDataPropertyAssertion]
