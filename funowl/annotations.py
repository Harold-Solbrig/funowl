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
from typing import Union, List, Callable, ClassVar, Tuple

from rdflib import URIRef, Graph
from rdflib.namespace import OWL, RDF, RDFS
from rdflib.term import BNode

from funowl.base.fun_owl_base import FunOwlBase
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.base.list_support import empty_list
from funowl.base.rdftriple import SUBJ, TRIPLE, PRED, TARG
from funowl.identifiers import IRI
from funowl.individuals import AnonymousIndividual
from funowl.literals import Literal
from funowl.terminals.TypingHelper import isinstance_
from funowl.writers.FunctionalWriter import FunctionalWriter


@dataclass
class AnnotationProperty(IRI):
    rdf_type: ClassVar[URIRef] = OWL.AnnotationProperty


@dataclass
class AnnotationSubject(FunOwlChoice):
    v: Union[IRI, AnonymousIndividual]



@dataclass
class AnnotationValue(FunOwlChoice):
    v: Union[AnonymousIndividual, IRI, Literal, str]
    input_type = str


# Placeholder to prevent recursive definitions
class Annotation(object):
    rdf_type = OWL.AnnotationProperty


@dataclass
class Annotatable(FunOwlBase, ABC):
    """ Annotatable must declare annotations after the required fields """

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

    def TANN(self, g: Graph, subj: Union[SUBJ, TRIPLE]) -> None:
        """
        TANN function as defined in https://www.w3.org/TR/2012/REC-owl2-mapping-to-rdf-20121211/#Translation_of_Annotations
        """
        # Tuple form means that we are annotating a triple:
        #  T(y) T(AP) T(av) .
        # _:x rdf:type owl:Annotation .
        # _:x owl:annotatedSource T(y) .
        # _:x owl:annotatedProperty T(AP) .
        # _:x owl:annotatedTarget T(av) .
        # TANN(annotation1, _:x)
        # ...
        # TANN(annotationn, _:x)
        if self.annotations:
            if isinstance(subj, Tuple):
                # Subj is a triple -- reify it
                x = BNode()
                g.add((x, RDF.type, OWL.Annotation))
                g.add((x, OWL.annotatedSource, subj[0]))
                g.add((x, OWL.annotatedProperty, subj[1]))
                g.add((x, OWL.annotatedTarget, subj[2]))
                subj = x

            for annotation in self.annotations:
                annotation.TANN(g, subj)

    def add_triple(self, g: Graph, subj: SUBJ, pred: PRED, obj: TARG) -> None:
        g.add((subj, pred, obj))
        self.TANN(g, (subj, pred, obj))


@dataclass
class Annotation(Annotatable):
    property: AnnotationProperty
    value: AnnotationValue
    annotations: List["Annotation"] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        # Annotated annotations get special handling
        return self.annots(w, lambda: w + self.property + self.value)

    def TANN(self, g: Graph, subj: Union[SUBJ, TRIPLE]) -> None:
        if isinstance_(subj, TRIPLE):
            g.add(subj)
            x = BNode()
            g.add((x, RDF.type, OWL.Annotation))
            g.add((x, OWL.annotatedSource, subj[0]))
            g.add((x, OWL.annotatedProperty, subj[1]))
            g.add((x, OWL.annotatedTarget, subj[2]))
            subj = x
        g.add((subj, self.property.to_rdf(g), self.value.to_rdf(g)))

@dataclass
class AnnotationAssertion(Annotatable):
    property: AnnotationProperty.types()
    subject: AnnotationSubject.types()
    value: AnnotationValue.types()
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.property + self.subject + self.value)

    def to_rdf(self, g: Graph) -> None:
        self.add_triple(g, self.subject.to_rdf(g), self.property.to_rdf(g), self.value.to_rdf(g))


@dataclass
class SubAnnotationPropertyOf(Annotatable):
    sub: AnnotationProperty
    super: AnnotationProperty
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.sub + self.super)

    def to_rdf(self, g: Graph) -> None:
        self.add_triple(g, self.sub.to_rdf(g), RDFS.subPropertyOf, self.super.to_rdf(g))


@dataclass
class AnnotationPropertyDomain(Annotatable):
    property: AnnotationProperty
    domain: IRI
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.property + self.domain)

    def to_rdf(self, g: Graph) -> None:
        self.add_triple(g, self.property.to_rdf(g), RDFS.domain, self.domain.to_rdf(g))


@dataclass
class AnnotationPropertyRange(Annotatable):
    property: AnnotationProperty
    range: IRI
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.property + self.range)

    def to_rdf(self, g: Graph) -> None:
        self.add_triple(g, self.property.to_rdf(g), RDFS.range, self.range.to_rdf(g))


AnnotationAxiom = Union[AnnotationAssertion, SubAnnotationPropertyOf, AnnotationPropertyDomain, AnnotationPropertyRange]
