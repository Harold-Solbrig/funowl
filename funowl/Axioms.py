"""
Axiom := Declaration | ClassAxiom | ObjectPropertyAxiom | DataPropertyAxiom | DatatypeDefinition |
         HasKey | Assertion | AnnotationAxiom

"""
from abc import ABC
from dataclasses import dataclass

from funowl.Annotations import Annotatable

@dataclass
class Axiom(Annotatable, ABC):
    pass

