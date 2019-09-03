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
from abc import ABC
from dataclasses import dataclass
from typing import Union, List, Callable, ClassVar

from rdflib import URIRef
from rdflib.namespace import OWL

from funowl.base.fun_owl_base import FunOwlBase
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.base.list_support import empty_list
from funowl.writers.FunctionalWriter import FunctionalWriter
from funowl.identifiers import IRI
from funowl.individuals import AnonymousIndividual
from funowl.literals import Literal


@dataclass
class AnnotationProperty(IRI):
    rdf_type: ClassVar[URIRef] = OWL.AnnotationProperty


@dataclass
class AnnotationSubject(FunOwlChoice):
    v: Union[IRI, AnonymousIndividual]


@dataclass
class AnnotationValue(FunOwlChoice):
    v: Union[AnonymousIndividual, IRI, Literal]


# Placeholder to prevent recursive definitions
class Annotation(object):
    rdf_type = OWL.AnnotationProperty


@dataclass
class Annotatable(FunOwlBase, ABC):
    """ Annotatable must redeclare annotations after the required fields """

    def _add_annotations(self, w: FunctionalWriter, f: Callable[[], FunctionalWriter] = None) -> FunctionalWriter:
        """
        Emit annotations at the beginnng of a functional declaration.  On entry, we've emitted "Func(" and
        need to emit zero or more "    Annotation( ... )" entries - one for each annotation
        :param w: FunctionalWriter to append output to
        :param f: function to generate everything within "func" after the annotations
        :return: FunctionalWriter instance
        """
        if self.annotations:
            w.br()
            w.iter(self.annotations, indent=False)
            w.br().indent()
        f()
        if self.annotations:
            w.outdent()
        return w

    def annots(self, w: FunctionalWriter, f: Callable[[], FunctionalWriter]) -> FunctionalWriter:
        """
        Emit the declaration of an annotatable function
        :param w: FunctionWriter
        :param f: function to generate post annotation function content
        :return: FUnctionWriter instance
        """
        return w.func(self, lambda: self._add_annotations(w, f))


@dataclass
class Annotation(Annotatable):
    property: AnnotationProperty
    value: AnnotationValue
    annotations: List["Annotation"] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        # Annotated annotations get special handling
        return self.annots(w, lambda: w + self.property + self.value)


class AnnotationAxiom(Annotatable):
    pass


@dataclass
class AnnotationAssertion(AnnotationAxiom):
    property: AnnotationProperty
    subject: AnnotationSubject
    value: AnnotationValue
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.property + self.subject + self.value)


@dataclass
class SubAnnotationPropertyOf(AnnotationAxiom):
    sub: AnnotationProperty
    super: AnnotationProperty
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.sub + self.super)


@dataclass
class AnnotationPropertyDomain(AnnotationAxiom):
    property: AnnotationProperty
    domain: IRI
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.property + self.domain)


@dataclass
class AnnotationPropertyRange(AnnotationAxiom):
    property: AnnotationProperty
    range: IRI
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.property + self.range)
