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

from funowl.annotations import AnnotationProperty
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.class_expressions import Class
from funowl.dataproperty_expressions import DataProperty
from funowl.individuals import NamedIndividual
from funowl.literals import Datatype
from funowl.objectproperty_expressions import ObjectProperty
from funowl.writers.FunctionalWriter import FunctionalWriter


# Class is defined in class_expressions.py

# Datatype is defined in literals.py

# ObjectProperty is defined in objectproperty_expressions.py

# DaataProperty is defined in dataproperty_expressions.py

# AnnotationProperty is defined in annotations.py

# NamedIndividual is defined in individuals.py


@dataclass
class Declaration(FunOwlChoice):
    v: Union[Class, Datatype, ObjectProperty, DataProperty, AnnotationProperty, NamedIndividual]
    _coercion_allowed = False

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w.func(self.v, lambda: self.v.to_functional(w), indent=False))
