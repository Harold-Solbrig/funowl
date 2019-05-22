"""
AnnotationSubject := IRI | AnonymousIndividual
AnnotationValue := AnonymousIndividual | IRI | Literal

Annotation := 'Annotation' '(' annotationAnnotations AnnotationProperty AnnotationValue ')'
annotationAnnotations  := { Annotation }

AnnotationAxiom := AnnotationAssertion | SubAnnotationPropertyOf | AnnotationPropertyDomain | AnnotationPropertyRange

AnnotationAssertion := 'AnnotationAssertion' '(' axiomAnnotations AnnotationProperty AnnotationSubject AnnotationValue ')'

SubAnnotationPropertyOf := 'SubAnnotationPropertyOf' '(' axiomAnnotations subAnnotationProperty superAnnotationProperty ')'
subAnnotationProperty := AnnotationProperty
superAnnotationProperty := AnnotationProperty

AnnotationPropertyDomain := 'AnnotationPropertyDomain' '(' axiomAnnotations AnnotationProperty IRI ')'

AnnotationPropertyRange := 'AnnotationPropertyRange' '(' axiomAnnotations AnnotationProperty IRI ')'
"""
from dataclasses import dataclass
from typing import Union, List, Callable, Optional

from funowl.FunOwlBase import FunOwlBase, empty_list, FunOwlChoice
from funowl.Identifiers import IRI
from funowl.Individuals import AnonymousIndividual
from funowl.Literals import Literal


@dataclass
class AnnotationSubject(FunOwlChoice):
    v: Union[IRI, AnonymousIndividual]


@dataclass
class AnnotationValue(FunOwlChoice):
    v: Union[AnonymousIndividual, IRI, Literal]


class AnnotationProperty(IRI):
    pass


class Annotatable(FunOwlBase):
    """ Annotatable must declare annotations after the required fields """

    def __init__(self, annotations: Optional[List["Annotation"]] = None):
        self.annotations = [] if annotations is None else self._cast(List[Annotation], annotations)

    def annots(self, indent: int, f: Callable[[int], str]) -> str:
        return self.func_name(indent, lambda i1: self.iter(i1, self.annotations) + f(indent))

    def list_cardinality(self, els: List["FunOwlBase"], list_name: str, min_: int = 1) -> "Annotatable":
        super().list_cardinality(els, list_name, min_)
        return self


@dataclass
class Annotation(Annotatable):
    property: AnnotationProperty
    value: AnnotationValue
    annotations: List["Annotation"] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent, lambda i1: self.property.as_owl() + ' ' + self.value.as_owl())


class AnnotationAxiom(Annotatable):
    pass


@dataclass
class AnnotationAssertion(AnnotationAxiom):
    property: AnnotationProperty
    subject: AnnotationSubject
    value: AnnotationValue
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent,
                           lambda i1: self.property.as_owl(i1) + self.subject.as_owl(i1) + self.value.as_owl())


@dataclass
class SubAnnotationPropertyOf(AnnotationAxiom):
    sub: AnnotationProperty
    super: AnnotationProperty
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent,
                           lambda i1: self.sub.as_owl(i1) + self.super.as_owl(i1))


@dataclass
class AnnotationPropertyDomain(AnnotationAxiom):
    property: AnnotationProperty
    domain: IRI
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent,
                           lambda i1: self.property.as_owl(i1) + self.domain.as_owl(i1))


@dataclass
class AnnotationPropertyRange(AnnotationAxiom):
    property: AnnotationProperty
    range: IRI
    annotations: List[Annotation] = empty_list()

    def as_owl(self, indent: int = 0) -> str:
        return self.annots(indent,
                           lambda i1: self.property.as_owl(i1) + self.range.as_owl(i1))
