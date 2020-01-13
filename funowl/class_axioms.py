"""
(Annotatable) := SubClassOf | EquivalentClasses | DisjointClasses | DisjointUnion

SubClassOf := 'SubClassOf' '(' axiomAnnotations subClassExpression superClassExpression ')'
subClassExpression := ClassExpression
superClassExpression := ClassExpression

EquivalentClasses := 'EquivalentClasses' '(' axiomAnnotations ClassExpression ClassExpression { ClassExpression } ')'

DisjointClasses := 'DisjointClasses' '(' axiomAnnotations ClassExpression ClassExpression { ClassExpression } ')'

DisjointUnion := 'DisjointUnion' '(' axiomAnnotations Class disjointClassExpressions ')'
disjointClassExpressions := ClassExpression ClassExpression { ClassExpression }
"""
from dataclasses import dataclass
from typing import List, Optional, Union

from rdflib import Graph, RDFS, OWL, RDF
from rdflib.term import Node, BNode

from funowl.annotations import Annotation, Annotatable
from funowl.base.list_support import empty_list
from funowl.class_expressions import ClassExpression, Class
from funowl.converters.rdf_converter import SEQ
from funowl.dataproperty_expressions import DataPropertyExpression
from funowl.objectproperty_expressions import ObjectPropertyExpression
from funowl.writers import FunctionalWriter


@dataclass
class SubClassOf(Annotatable):
    subClassExpression: ClassExpression
    superClassExpression: ClassExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: (w + self.subClassExpression + self.superClassExpression))

    def to_rdf(self, g: Graph) -> None:
        """
        Add subclass representation to graph
        :param g: Graph to add representation to
        :return: None -
        """
        self.add_triple(g, self.subClassExpression.to_rdf(g), RDFS.subClassOf, self.superClassExpression.to_rdf(g))


@dataclass
class EquivalentClasses(Annotatable):
    classExpressions: List[ClassExpression]
    annotations: List[Annotation] = empty_list()

    def __init__(self, *classExpression: ClassExpression, annotations: List[Annotation] = None) -> None:
        self.classExpressions = list(classExpression)
        self.annotations = annotations or []

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.classExpressions, 'classExpressions', 2)
        return self.annots(w, lambda: w.iter(self.classExpressions))

    def to_rdf(self, g: Graph) -> None:
        # EquivalentClasses( CE1 ... CEn ) 	T(CE1) owl:equivalentClass T(CE2) .
        # ...
        # T(CEn-1) owl:equivalentClass T(CEn) .
        for ce1, ce2 in zip(self.classExpressions[:-1], self.classExpressions[1:]):
            self.add_triple(g, ce1.to_rdf(g), OWL.equivalentClass, ce2.to_rdf(g))


@dataclass
class DisjointClasses(Annotatable):
    classExpressions: List[ClassExpression]
    annotations: List[Annotation] = empty_list()

    def __init__(self, *classExpression: ClassExpression, annotations: List[Annotation] = None) -> None:
        self.classExpressions = list(classExpression)
        self.annotations = annotations or []
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.classExpressions, 'classExpressions', 2)
        if len(self.classExpressions) == 2:
            return self.annots(w, lambda: w + self.classExpressions[0] + self.classExpressions[1])
        else:
            return self.annots(w, lambda: w.iter(self.classExpressions))

    def to_rdf(self, g: Graph) -> None:
        if len(self.classExpressions) == 2:
            self.add_triple(g, self.classExpressions[0].to_rdf(g),
                            OWL.disjointWith, self.classExpressions[1].to_rdf(g))
        else:
            subj = BNode()
            g.add((subj, RDF.type, OWL.AllDisjointClasses))
            g.add((subj, OWL.members, SEQ(g, self.classExpressions)))
            self.TANN(g, subj)


@dataclass
class DisjointUnion(Annotatable):
    cls: Class
    disjointClassExpressions: List[ClassExpression]
    annotations: List[Annotation] = empty_list()

    def __init__(self, cls: Class, *disjointClassExpression: ClassExpression,
                 annotations: List[Annotation] = None) -> None:
        self.cls = cls
        self.disjointClassExpressions = list(disjointClassExpression)
        self.annotations = annotations or []
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.disjointClassExpressions, 'disjointClassExpressions', 2)
        return self.annots(w, lambda: (w + self.cls).iter(self.disjointClassExpressions))

    def to_rdf(self, g: Graph) -> None:
        # 	T(C) owl:disjointUnionOf T(SEQ CE1 ... CEn) .
        self.add_triple(g, self.cls.to_rdf(g), OWL.disjointUnionOf, SEQ(g, self.disjointClassExpressions))

@dataclass
class HasKey(Annotatable):
    classExpression: ClassExpression
    objectPropertyExpressions: Optional[List[ObjectPropertyExpression]] = empty_list()
    dataPropertyExpressions: Optional[List[DataPropertyExpression]] = empty_list()
    annotations: List[Annotation] = empty_list()

    def __init__(self, classExpression: ClassExpression,
                 *exprs: Union[ObjectPropertyExpression, DataPropertyExpression],
                 annotations: List[Annotation] = None):
        self.classExpression = classExpression
        self.objectPropertyExpressions = []
        self.dataPropertyExpressions = []
        for expr in exprs:
            if isinstance(expr, ObjectPropertyExpression):
                self.objectPropertyExpressions.append(expr)
            else:
                self.dataPropertyExpressions.append(expr)
        self.annotations = annotations or []
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w,
                           lambda: ((w + self.classExpression +
                                    '(').iter(self.objectPropertyExpressions) + ')' +
                                    '(').iter(self.dataPropertyExpressions) + ')')

    def to_rdf(self, g: Graph) -> None:
        # T(CE) owl:hasKey T(SEQ OPE1 ... OPEm DPE1 ... DPEn ) .
        self.add_triple(g, self.classExpression.to_rdf(g), OWL.hasKey,
                        SEQ(g, self.objectPropertyExpressions + self.dataPropertyExpressions))


ClassAxiom = Union[SubClassOf, EquivalentClasses, DisjointClasses, DisjointUnion]