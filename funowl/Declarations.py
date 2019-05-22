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
from typing import Union

from funowl.Annotations import Annotatable, AnnotationProperty
from funowl.Axioms import Axiom
from funowl.FunOwlBase import FunOwlChoice, FunOwlBase
from funowl.Identifiers import IRIType, IRI
from funowl.Individuals import NamedIndividual


class Class(IRI):
    pass


class Datatype(IRI):
    pass


class ObjectProperty(IRI):
    pass


class InverseObjectProperty(FunOwlBase):
    v : ObjectProperty

    def __init__(self, v) -> None:
        self.v = v

    def as_owl(self, indent: int = 0) -> str:
        return self.i(indent) + self.v.as_owl()


class ObjectPropertyExpression(FunOwlChoice):
    v : Union[ObjectProperty, InverseObjectProperty]


class DataProperty(IRIType):
    pass


class DataPropertyExpression(DataProperty):
    pass


class Declaration(Axiom):
    v: Union[Class, Datatype, ObjectProperty, DataProperty, AnnotationProperty, NamedIndividual]

    def __init__(self,
                 v: Union[Class, Datatype, ObjectProperty, DataProperty, AnnotationProperty, NamedIndividual]) -> None:
        self.v = v

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.v.as_owl(indent))
