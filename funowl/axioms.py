"""
Axiom := Declaration | ClassAxiom | ObjectPropertyAxiom | DataPropertyAxiom | DatatypeDefinition |
         HasKey | Assertion | AnnotationAxiom

"""
from typing import Union

from rdflib import OWL

from funowl.annotations import AnnotationAxiom, Annotatable
from funowl.assertions import Assertion
from funowl.class_axioms import ClassAxiom, HasKey
from funowl.dataproperty_axioms import DataPropertyAxiom, DatatypeDefinition
from funowl.declarations import Declaration
from funowl.objectproperty_axioms import ObjectPropertyAxiom

Axiom = Union[Declaration, ClassAxiom, ObjectPropertyAxiom, DataPropertyAxiom, DatatypeDefinition, HasKey, Assertion,
              AnnotationAxiom]
