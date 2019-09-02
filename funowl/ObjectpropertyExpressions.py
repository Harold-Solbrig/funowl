from dataclasses import dataclass
from typing import Union

from rdflib import OWL

from funowl.Identifiers import IRI
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.writers import FunctionalWriter


@dataclass
class ObjectProperty(IRI):
    rdf_type = OWL.ObjectProperty


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
