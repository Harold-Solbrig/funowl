"""
ClassExpression :=
    Class |
    ObjectIntersectionOf | ObjectUnionOf | ObjectComplementOf | ObjectOneOf |
    ObjectSomeValuesFrom | ObjectAllValuesFrom | ObjectHasValue | ObjectHasSelf |
    ObjectMinCardinality | ObjectMaxCardinality | ObjectExactCardinality |
    DataSomeValuesFrom | DataAllValuesFrom | DataHasValue |
    DataMinCardinality | DataMaxCardinality | DataExactCardinality

ObjectIntersectionOf := 'ObjectIntersectionOf' '(' ClassExpression ClassExpression { ClassExpression } ')'

ObjectUnionOf := 'ObjectUnionOf' '(' ClassExpression ClassExpression { ClassExpression } ')'

ObjectComplementOf := 'ObjectComplementOf' '(' ClassExpression ')'

ObjectOneOf := 'ObjectOneOf' '(' Individual { Individual }')'

ObjectSomeValuesFrom := 'ObjectSomeValuesFrom' '(' ObjectPropertyExpression ClassExpression ')'

ObjectAllValuesFrom := 'ObjectAllValuesFrom' '(' ObjectPropertyExpression ClassExpression ')'

ObjectHasValue := 'ObjectHasValue' '(' ObjectPropertyExpression Individual ')'

ObjectHasSelf := 'ObjectHasSelf' '(' ObjectPropertyExpression ')'

ObjectMinCardinality := 'ObjectMinCardinality' '(' nonNegativeInteger ObjectPropertyExpression [ ClassExpression ] ')'

ObjectMaxCardinality := 'ObjectMaxCardinality' '(' nonNegativeInteger ObjectPropertyExpression [ ClassExpression ] ')'

ObjectExactCardinality := 'ObjectExactCardinality' '(' nonNegativeInteger ObjectPropertyExpression [ ClassExpression ] ')'

DataSomeValuesFrom := 'DataSomeValuesFrom' '(' DataPropertyExpression { DataPropertyExpression } DataRange ')'

DataAllValuesFrom := 'DataAllValuesFrom' '(' DataPropertyExpression { DataPropertyExpression } DataRange ')'

DataHasValue := 'DataHasValue' '(' DataPropertyExpression Literal ')'

DataMinCardinality := 'DataMinCardinality' '(' nonNegativeInteger DataPropertyExpression [ DataRange ] ')'

DataMaxCardinality := 'DataMaxCardinality' '(' nonNegativeInteger DataPropertyExpression [ DataRange ] ')'

DataExactCardinality := 'DataExactCardinality' '(' nonNegativeInteger DataPropertyExpression [ DataRange ] ')'

HasKey := 'HasKey' '(' axiomAnnotations ClassExpression '(' { ObjectPropertyExpression } ')' '(' { DataPropertyExpression } ')' ')'
"""
from dataclasses import dataclass
from typing import List, ClassVar, Union, Optional

from rdflib import URIRef, OWL, Graph, RDF
from rdflib.term import BNode, Literal as RDFLiteral

from funowl.base.fun_owl_base import FunOwlBase
from funowl.converters.rdf_converter import SEQ
from funowl.dataproperty_expressions import DataPropertyExpression
from funowl.dataranges import DataRange
from funowl.general_definitions import NonNegativeInteger
from funowl.identifiers import IRI
from funowl.individuals import Individual
from funowl.literals import Literal
from funowl.objectproperty_expressions import ObjectPropertyExpression
from funowl.writers import FunctionalWriter


class Class(IRI):
    rdf_type: ClassVar[URIRef] = OWL.Class


@dataclass
class ObjectIntersectionOf(FunOwlBase):
    classExpressions: List["ClassExpression"]

    def __init__(self, *classExpression: "ClassExpression") -> None:
        self.classExpressions = list(classExpression)
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.classExpressions, 'exprs', 2)
        return w.func(self, lambda: w.iter(self.classExpressions))

    def to_rdf(self, g: Graph) -> BNode:
        subj = BNode()
        g.add((subj, RDF.type, OWL.Class))
        g.add((subj, OWL.intersectionOf, SEQ(g, self.classExpressions)))
        return subj


@dataclass
class ObjectUnionOf(FunOwlBase):
    classExpressions: List["ClassExpression"]

    def __init__(self, *classExpression: "ClassExpression") -> None:
        self.classExpressions = list(classExpression)
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.classExpressions, 'exprs', 2)
        return w.func(self, lambda: w.iter(self.classExpressions))

    def to_rdf(self, g: Graph) -> BNode:
        """
        _:x rdf:type owl:Class .
        _:x owl:unionOf T(SEQ CE1 ... CEn) .
        """
        rval = BNode()
        g.add((rval, RDF.type, OWL.Class))
        g.add((rval, OWL.unionOf, SEQ(g, self.classExpressions)))
        return rval

@dataclass
class ObjectComplementOf(FunOwlBase):
    classExpression: "ClassExpression"

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.classExpression)


@dataclass(init=False)
class ObjectOneOf(FunOwlBase):
    individuals: List[Individual.types()]

    def __init__(self, *individual: Individual) -> None:
        self.individuals = list(individual)
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w.iter(self.individuals))

    def to_rdf(self, g: Graph) -> BNode:
        """
        _:x rdf:type owl:Class .
        _:x owl:oneOf T(SEQ a1 ... an) .
        :param g:
        :return:
        """
        rval = BNode()
        g.add((rval, RDF.type, OWL.Class))
        g.add((rval, OWL.oneOf, SEQ(g, self.individuals)))
        return rval


@dataclass
class ObjectSomeValuesFrom(FunOwlBase):
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: "ClassExpression"
    coercion_allowed: ClassVar[bool] = True

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.objectPropertyExpression + self.classExpression)

    def to_rdf(self, g: Graph) -> BNode:
        """
        :x rdf:type owl:Restriction .
        _:x owl:onProperty T(OPE) .
        _:x owl:someValuesFrom T(CE) .
        :param g: the RDF graph
        :return: a BNode
        """
        rval = BNode()
        g.add((rval, RDF.type, OWL.Restriction))
        g.add((rval, OWL.onProperty, self.objectPropertyExpression.to_rdf(g)))
        g.add((rval, OWL.someValuesFrom, self.classExpression.to_rdf(g)))
        return rval


@dataclass
class ObjectAllValuesFrom(FunOwlBase):
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: "ClassExpression"

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.objectPropertyExpression + self.classExpression)

    def to_rdf(self, g: Graph) -> BNode:
        """
        _:x rdf:type owl:Restriction .
        _:x owl:onProperty T(OPE) .
        _:x owl:allValuesFrom T(CE) .
        :param g: RDF graph
        :return: a BNode
        """
        rval = BNode()
        g.add((rval, RDF.type, OWL.Restriction))
        g.add((rval, OWL.onProperty, self.objectPropertyExpression.to_rdf(g)))
        g.add((rval, OWL.allValuesFrom, self.classExpression.to_rdf(g)))
        return rval


@dataclass
class ObjectHasValue(FunOwlBase):
    objectPropertyExpression: ObjectPropertyExpression
    individual: Individual

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.objectPropertyExpression + self.individual)

    def to_rdf(self, g: Graph) -> BNode:
        """
        _:x rdf:type owl:Restriction .
        _:x owl:onProperty T(OPE) .
        _:x owl:hasValue T(a) .
        """
        rval = BNode()
        g.add((rval, RDF.type, OWL.Restriction))
        g.add((rval, OWL.onProperty, self.objectPropertyExpression.to_rdf(g)))
        g.add((rval, OWL.hasValue, self.individual.to_rdf(g)))
        return rval


@dataclass
class ObjectHasSelf(FunOwlBase):
    objectPropertyExpression: ObjectPropertyExpression

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.objectPropertyExpression)

    def to_rdf(self, g: Graph) -> BNode:
        """
        _:x rdf:type owl:Restriction .
        _:x owl:onProperty T(OPE) .
        _:x owl:hasSelf "true"^^xsd:boolean .
        :param g: the RDF graph
        :return: a BNode
        """
        rval = BNode()
        g.add((rval, RDF.type, OWL.Restriction))
        g.add((rval, OWL.onProperty, self.objectPropertyExpression.to_rdf(g)))
        g.add((rval, OWL.hasSelf, RDFLiteral(True)))
        return rval


@dataclass
class ObjectMinCardinality(FunOwlBase):
    min_: NonNegativeInteger
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: Optional["ClassExpression"] = None

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.min_ + self.objectPropertyExpression).opt(self.classExpression))


@dataclass
class ObjectMaxCardinality(FunOwlBase):
    max_: NonNegativeInteger
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: Optional["ClassExpression"] = None

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.max_ + self.objectPropertyExpression).opt(self.classExpression))


@dataclass
class ObjectExactCardinality(FunOwlBase):
    card: NonNegativeInteger
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: Optional["ClassExpression"] = None

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.card + self.objectPropertyExpression).opt(self.classExpression))

    def to_rdf(self, g: Graph) -> BNode:
        """
        _:x rdf:type owl:Restriction .
        _:x owl:onProperty T(OPE) .
        _:x owl:cardinality "n"^^xsd:nonNegativeInteger .
        """
        rval = BNode()
        ...
        return rval


@dataclass
class DataSomeValuesFrom(FunOwlBase):
    dataPropertyExpression: DataPropertyExpression
    dataRange: DataRange

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.dataPropertyExpression + self.dataRange))


@dataclass
class DataAllValuesFrom(FunOwlBase):
    dataPropertyExpression: DataPropertyExpression
    dataRange: DataRange

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.dataPropertyExpression + self.dataRange))


@dataclass
class DataHasValue(FunOwlBase):
    dataPropertyExpression: DataPropertyExpression
    literal: Literal

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.dataPropertyExpression + self.literal))


@dataclass
class DataMinCardinality(FunOwlBase):
    min_: NonNegativeInteger
    dataPropertyExpression: DataPropertyExpression
    dataRange: Optional[DataRange] = None

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.min_ + self.dataPropertyExpression).opt(self.dataRange))


@dataclass
class DataMaxCardinality(FunOwlBase):
    max_: NonNegativeInteger
    dataPropertyExpression: DataPropertyExpression
    dataRange: Optional[DataRange] = None

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.max_ + self.dataPropertyExpression).opt(self.dataRange))


@dataclass
class DataExactCardinality(FunOwlBase):
    card: NonNegativeInteger
    dataPropertyExpression: DataPropertyExpression
    dataRange: Optional[DataRange] = None

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.card + self.dataPropertyExpression).opt(self.dataRange))


# A Class expression can be a class or any subclass of ClassExpression
# @dataclass
# class ClassExpression(FunOwlBase):
ClassExpression = Union[Class, ObjectIntersectionOf, ObjectUnionOf, ObjectComplementOf, ObjectOneOf,
    ObjectSomeValuesFrom, ObjectAllValuesFrom, ObjectHasValue, ObjectHasSelf,
    ObjectMinCardinality, ObjectMaxCardinality, ObjectExactCardinality,
    DataSomeValuesFrom, DataAllValuesFrom, DataHasValue,
    DataMinCardinality, DataMaxCardinality, DataExactCardinality]
