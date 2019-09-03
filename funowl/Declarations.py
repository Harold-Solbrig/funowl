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
from typing import Union

from rdflib import Graph

from funowl.annotations import AnnotationProperty
from funowl.Axioms import Axiom
from funowl.ClassExpressions import Class
from funowl.DatapropertyExpressions import DataProperty
from funowl.Individuals import NamedIndividual
from funowl.Literals import Datatype
from funowl.ObjectpropertyExpressions import ObjectProperty
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.writers.FunctionalWriter import FunctionalWriter


# Class is defined in ClassExpressions.py

# Datatype is defined in Literals.py

# ObjectProperty is defined in ObjectpropertyExpressions.py

# DaataProperty is defined in DatapropertyExpressions.py

# AnnotationProperty is defined in annotations.py

# NamedIndividual is defined in Individuals.py


@dataclass
class Declaration(Axiom, FunOwlChoice):
    v: Union[Class, Datatype, ObjectProperty, DataProperty, AnnotationProperty, NamedIndividual]
    coercion_allowed = False

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w.func(self.v, lambda: self.v.to_functional(w)))

    def to_rdf(self, g: Graph) -> None:
        self.v.to_rdf(g)
