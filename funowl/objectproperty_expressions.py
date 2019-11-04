from dataclasses import dataclass
from typing import Union

from rdflib import OWL

from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.identifiers import IRI
from funowl.writers import FunctionalWriter


@dataclass
class ObjectProperty(IRI):
    rdf_type = OWL.ObjectProperty


@dataclass
class ObjectInverseOf(FunOwlChoice):
    v: Union[ObjectProperty, str]
    input_type = str

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.v)


@dataclass
class ObjectPropertyExpression(FunOwlChoice):
    # The order below is important
    v: Union[ObjectProperty, ObjectInverseOf, str]
    coercion_allowed = False
    input_type = str

