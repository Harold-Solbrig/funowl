"""
Declaration := 'Declaration' '(' axiomAnnotations Entity ')'
Entity :=
    'Class' '(' Class ')' |
    'Datatype' '(' Datatype ')' |
    'ObjectProperty' '(' ObjectProperty ')' |
    'DataProperty' '(' DataProperty ')' |
    'AnnotationProperty' '(' AnnotationProperty ')' |
    'NamedIndividual' '(' NamedIndividual ')'

ObjectPropertyExpression := ObjectProperty | InverseObjectProperty

InverseObjectProperty := 'ObjectInverseOf' '(' ObjectProperty ')'

DataPropertyExpression := DataProperty
"""
from dataclasses import dataclass
from typing import Union, ClassVar, Tuple

from rdflib import Graph, OWL, URIRef

from funowl.Annotations import AnnotationProperty
from funowl.Axioms import Axiom
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.writers.FunctionalWriter import FunctionalWriter
from funowl.Identifiers import IRI
from funowl.Individuals import NamedIndividual
from funowl.Literals import Datatype


@dataclass
class Class(IRI):
    rdf_type: ClassVar[URIRef] = OWL.Class


# Datatype is defined in Literals.py


@dataclass
class ObjectProperty(IRI):
    rdf_type = OWL.ObjectProperty


@dataclass
class DataProperty(IRI):
    rdf_type = OWL.DatatypeProperty

# AnnotationProperty is defined in Annotations.py

# NamedIndividual is defined in Individuals.py

@dataclass
class ObjectInverseOf(FunOwlChoice):
    v: Union[ObjectProperty]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.v)

@dataclass
class ObjectPropertyExpression(FunOwlChoice):
    # The order below is important
    v: Union[ObjectProperty, ObjectInverseOf]
    coercion_allowed = False


# DataPropertyExpression is just a synonym for dataproperty
@dataclass
class DataPropertyExpression(DataProperty):
    pass


@dataclass
class Declaration(Axiom, FunOwlChoice):
    v: Union[Class, Datatype, ObjectProperty, DataProperty, AnnotationProperty, NamedIndividual]
    coercion_allowed = False

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w.func(self.v, lambda: self.v.to_functional(w)))

    def to_rdf(self, g: Graph) -> None:
        self.v.to_rdf(g)
