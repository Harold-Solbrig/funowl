"""
ObjectPropertyAxiom :=
    SubObjectPropertyOf | EquivalentObjectProperties |
    DisjointObjectProperties | InverseObjectProperties |
    ObjectPropertyDomain | ObjectPropertyRange |
    FunctionalObjectProperty | InverseFunctionalObjectProperty |
    ReflexiveObjectProperty | IrreflexiveObjectProperty |
    SymmetricObjectProperty | AsymmetricObjectProperty |
    TransitiveObjectProperty

SubObjectPropertyOf := 'SubObjectPropertyOf' '(' axiomAnnotations subObjectPropertyExpression superObjectPropertyExpression ')'
subObjectPropertyExpression := ObjectPropertyExpression | propertyExpressionChain
propertyExpressionChain := 'ObjectPropertyChain' '(' ObjectPropertyExpression ObjectPropertyExpression { ObjectPropertyExpression } ')'
superObjectPropertyExpression := ObjectPropertyExpression

EquivalentObjectProperties := 'EquivalentObjectProperties' '(' axiomAnnotations ObjectPropertyExpression ObjectPropertyExpression { ObjectPropertyExpression } ')'

DisjointObjectProperties := 'DisjointObjectProperties' '(' axiomAnnotations ObjectPropertyExpression ObjectPropertyExpression { ObjectPropertyExpression } ')'

ObjectPropertyDomain := 'ObjectPropertyDomain' '(' axiomAnnotations ObjectPropertyExpression ClassExpression ')'

ObjectPropertyRange := 'ObjectPropertyRange' '(' axiomAnnotations ObjectPropertyExpression ClassExpression ')'

InverseObjectProperties := 'InverseObjectProperties' '(' axiomAnnotations ObjectPropertyExpression ObjectPropertyExpression ')'

FunctionalObjectProperty := 'FunctionalObjectProperty' '(' axiomAnnotations ObjectPropertyExpression ')'

InverseFunctionalObjectProperty := 'InverseFunctionalObjectProperty' '(' axiomAnnotations ObjectPropertyExpression ')'

ReflexiveObjectProperty := 'ReflexiveObjectProperty' '(' axiomAnnotations ObjectPropertyExpression ')'

IrreflexiveObjectProperty := 'IrreflexiveObjectProperty' '(' axiomAnnotations ObjectPropertyExpression ')'

SymmetricObjectProperty := 'SymmetricObjectProperty' '(' axiomAnnotations ObjectPropertyExpression ')'

AsymmetricObjectProperty := 'AsymmetricObjectProperty' '(' axiomAnnotations ObjectPropertyExpression ')'

TransitiveObjectProperty := 'TransitiveObjectProperty' '(' axiomAnnotations ObjectPropertyExpression ')'
"""
from dataclasses import dataclass
from typing import List, Union, Optional

from rdflib import Graph, BNode, OWL, RDF, RDFS

from funowl.annotations import Annotation, Annotatable
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.base.list_support import empty_list
from funowl.class_expressions import ClassExpression
from funowl.base.fun_owl_base import FunOwlBase
from funowl.converters.rdf_converter import SEQ
from funowl.objectproperty_expressions import ObjectPropertyExpression
from funowl.writers.FunctionalWriter import FunctionalWriter


@dataclass
class ObjectPropertyChain(Annotatable):
    objectPropertyExpressions: List[ObjectPropertyExpression]
    annotations: List[Annotation] = empty_list()

    def __init__(self, *objectPropertyExpressions: ObjectPropertyExpression, annotations: List[Annotation] = None):
        self.objectPropertyExpressions = list(objectPropertyExpressions)
        self.annotations = annotations if annotations else []
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w.iter(self.objectPropertyExpressions))

    def to_rdf(self, g: Graph) -> BNode:
        return SEQ(g, self.objectPropertyExpressions)

@dataclass
class SubObjectPropertyExpression(FunOwlChoice):
    v: Union[ObjectPropertyExpression.types(), ObjectPropertyChain]


@dataclass
class SubObjectPropertyOf(Annotatable):
    subObjectPropertyExpression: SubObjectPropertyExpression.types()
    superObjectPropertyExpression: ObjectPropertyExpression.types()
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: (w + self.subObjectPropertyExpression + self.superObjectPropertyExpression))

    def to_rdf(self, g: Graph) -> None:
        if issubclass(type(self.subObjectPropertyExpression), ObjectPropertyChain):
            self.add_triple(g, self.superObjectPropertyExpression.to_rdf(g), OWL.propertyChainAxiom,
                            self.subObjectPropertyExpression.to_rdf(g))
        else:
            self.add_triple(g, self.subObjectPropertyExpression.to_rdf(g), RDFS.subPropertyOf,
                            self.superObjectPropertyExpression.to_rdf(g))


@dataclass
class EquivalentObjectProperties(Annotatable):
    objectPropertyExpressions: List[ObjectPropertyExpression]
    annotations: List[Annotation] = empty_list()

    def __init__(self, *objectPropertyExpressions: ObjectPropertyExpression,
                 annotations: Optional[List[Annotation]] = None) -> None:
        self.objectPropertyExpressions = list(objectPropertyExpressions)
        self.annotations = annotations or []
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w.iter(self.objectPropertyExpressions))

    def to_rdf(self, g: Graph) -> None:
        for t1, t2 in zip(self.objectPropertyExpressions[:-1], self.objectPropertyExpressions[1:]):
            self.add_triple(g, t1.to_rdf(g), OWL.equivalentProperty, t2.to_rdf(g))

@dataclass
class DisjointObjectProperties(Annotatable):
    objectPropertyExpressions: List[ObjectPropertyExpression]
    annotations: List[Annotation] = empty_list()

    def __init__(self, *objectPropertyExpressions: ObjectPropertyExpression,
                 annotations: Optional[List[Annotation]] = None) -> None:
        self.objectPropertyExpressions = list(objectPropertyExpressions)
        self.annotations = annotations or []
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w.iter(self.objectPropertyExpressions))

    def to_rdf(self, g: Graph) -> None:
        # T(OPE1) owl:propertyDisjointWith T(OPE2) .
        # N > 2:
        #    _:x rdf:type owl:AllDisjointProperties .
        #    _:x owl:members T(SEQ OPE1 ... OPEn) .
        if len(self.objectPropertyExpressions) > 2:
            x = BNode()
            g.add((x, RDF.type, OWL.AllDisjointProperties))
            self.add_triple(g, x, OWL.members, SEQ(g, self.objectPropertyExpressions))
        else:
            self.add_triple(g, self.objectPropertyExpressions[0].to_rdf(g), OWL.propertyDisjointWith,
                            self.objectPropertyExpressions[1].to_rdf(g))

@dataclass
class ObjectPropertyDomain(Annotatable):
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: ClassExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.objectPropertyExpression + self.classExpression)

    def to_rdf(self, g: Graph) -> None:
        # T(OPE) rdfs:domain T(CE) .
        self.add_triple(g, self.objectPropertyExpression.to_rdf(g), RDFS.domain, self.classExpression.to_rdf(g))

@dataclass
class ObjectPropertyRange(Annotatable):
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: ClassExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.objectPropertyExpression + self.classExpression)

    def to_rdf(self, g: Graph) -> None:
        # T(OPE) rdfs:range T(CE) .
        self.add_triple(g, self.objectPropertyExpression.to_rdf(g), RDFS.range, self.classExpression.to_rdf(g))


@dataclass
class InverseObjectProperties(Annotatable):
    objectPropertyExpressions: List[ObjectPropertyExpression]
    annotations: List[Annotation] = empty_list()

    def __init__(self, *objectPropertyExpressions: ObjectPropertyExpression, annotations: List[Annotation] = None) \
            -> None:
        self.objectPropertyExpressions = list(objectPropertyExpressions)
        self.annotations = annotations or []

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.objectPropertyExpressions, 'expressions', 2, 2)
        return w.func(self, lambda: w + self.objectPropertyExpressions[0] + self.objectPropertyExpressions[1])

    def to_rdf(self, g: Graph) -> None:
        g.add((self.objectPropertyExpressions[0].to_rdf(g), OWL.inverseOf, self.objectPropertyExpressions[1].to_rdf(g)))

@dataclass
class FunctionalObjectProperty(Annotatable):
    objectPropertyExpression: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.objectPropertyExpression)

    def to_rdf(self, g: Graph) -> None:
        g.add((self.objectPropertyExpression.to_rdf(g), RDF.type, OWL.FunctionalProperty))


@dataclass
class InverseFunctionalObjectProperty(Annotatable):
    objectPropertyExpression: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.objectPropertyExpression)

    def to_rdf(self, g: Graph) -> None:
        g.add((self.objectPropertyExpression.to_rdf(g), RDF.type, OWL.InverseFunctionalProperty))


@dataclass
class ReflexiveObjectProperty(Annotatable):
    objectPropertyExpression: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.objectPropertyExpression)

    def to_rdf(self, g: Graph) -> None:
        # T(OPE) rdf:type owl:ReflexiveProperty .
        self.add_triple(g, self.objectPropertyExpression.to_rdf(g), RDF.type, OWL.ReflexiveProperty)


@dataclass
class IrreflexiveObjectProperty(Annotatable):
    objectPropertyExpression: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.objectPropertyExpression)

    def to_rdf(self, g: Graph) -> None:
        # T(OPE) rdf:type owl:IrreflexiveProperty .
        self.add_triple(g, self.objectPropertyExpression.to_rdf(g), RDF.type, OWL.IrreflexiveProperty)


@dataclass
class SymmetricObjectProperty(Annotatable):
    objectPropertyExpression: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.objectPropertyExpression)

    def to_rdf(self, g: Graph) -> None:
        # T(OPE) rdf:type owl:SymmetricProperty .
        self.add_triple(g, self.objectPropertyExpression.to_rdf(g), RDF.type, OWL.SymmetricProperty)


@dataclass
class AsymmetricObjectProperty(Annotatable):
    objectPropertyExpression: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.objectPropertyExpression)

    def to_rdf(self, g: Graph) -> None:
        # T(OPE) rdf:type owl:AsymmetricProperty .
        self.add_triple(g, self.objectPropertyExpression.to_rdf(g), RDF.type, OWL.AsymmetricProperty)


@dataclass
class TransitiveObjectProperty(Annotatable):
    objectPropertyExpression: ObjectPropertyExpression
    annotations: List[Annotation] = empty_list()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return self.annots(w, lambda: w + self.objectPropertyExpression)

    def to_rdf(self, g: Graph) -> None:
        # T(OPE) rdf:type owl:TransitiveProperty .
        self.add_triple(g, self.objectPropertyExpression.to_rdf(g), RDF.type, OWL.TransitiveProperty)


ObjectPropertyAxiom = Union[SubObjectPropertyOf, EquivalentObjectProperties, DisjointObjectProperties,
                            InverseObjectProperties, ObjectPropertyDomain, ObjectPropertyRange,
                            FunctionalObjectProperty, InverseFunctionalObjectProperty, ReflexiveObjectProperty,
                            IrreflexiveObjectProperty, SymmetricObjectProperty, AsymmetricObjectProperty,
                            TransitiveObjectProperty ]
