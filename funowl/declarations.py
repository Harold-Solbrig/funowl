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
from typing import Union, List, Optional

from rdflib import Graph

from funowl.annotations import AnnotationProperty, Annotatable, Annotation
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.base.list_support import empty_list_wrapper
from funowl.base.rdftriple import NODE, SUBJ
from funowl.class_expressions import Class
from funowl.dataproperty_expressions import DataProperty
from funowl.individuals import NamedIndividual
from funowl.literals import Datatype
from funowl.objectproperty_expressions import ObjectProperty
from funowl.writers.FunctionalWriter import FunctionalWriter


@dataclass
class Declaration(FunOwlChoice, Annotatable):
    v: Union[Class, Datatype, ObjectProperty, DataProperty, AnnotationProperty, NamedIndividual]
    annotations: List[Annotation] = empty_list_wrapper(Annotation)
    _coercion_allowed = False

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w.func(self.v, lambda: self.v.to_functional(w), indent=False))

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> Optional[NODE]:
        return super().to_rdf(g, emit_type_arc=True)
