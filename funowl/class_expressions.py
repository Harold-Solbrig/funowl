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

from rdflib import URIRef, OWL

from funowl.dataranges import DataRange
from funowl.dataproperty_expressions import DataPropertyExpression
from funowl.general_definitions import NonNegativeInteger
from funowl.identifiers import IRI
from funowl.individuals import Individual
from funowl.literals import Literal
from funowl.objectproperty_expressions import ObjectPropertyExpression
from funowl.base.fun_owl_base import FunOwlBase
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


@dataclass
class ObjectUnionOf(FunOwlBase):
    classExpressions: List["ClassExpression"]

    def __init__(self, *classExpression: "ClassExpression") -> None:
        self.classExpressions = list(classExpression)
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.classExpressions, 'exprs', 2)
        return w.func(self, lambda: w.iter(self.classExpressions))


@dataclass
class ObjectComplementOf(FunOwlBase):
    classExpression: "ClassExpression"

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.classExpression)


@dataclass(init=False)
class ObjectOneOf(FunOwlBase):
    individuals: List[Individual]

    def __init__(self, *individual: Individual) -> None:
        self.individuals = list(individual)
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.exprs, 'exprs', 2)
        return w.func(self, lambda: w.iter(self.individuals))


@dataclass
class ObjectSomeValuesFrom(FunOwlBase):
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: "ClassExpression"
    coercion_allowed: ClassVar[bool] = True

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.objectPropertyExpression + self.classExpression)


@dataclass
class ObjectAllValuesFrom(FunOwlBase):
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: "ClassExpression"

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.objectPropertyExpression + self.classExpression)


@dataclass
class ObjectHasValue(FunOwlBase):
    objectPropertyExpression: ObjectPropertyExpression
    individual: Individual

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.objectPropertyExpression + self.individual)


@dataclass
class ObjectHasSelf(FunOwlBase):
    objectPropertyExpression: ObjectPropertyExpression

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.objectPropertyExpression)


@dataclass
class ObjectMinCardinality(FunOwlBase):
    min_: NonNegativeInteger
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: Optional["ClassExpression"]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.min_ + self.objectPropertyExpression).opt(self.classExpression))


@dataclass
class ObjectMaxCardinality(FunOwlBase):
    max_: NonNegativeInteger
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: Optional["ClassExpression"]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.max_ + self.objectPropertyExpression).opt(self.classExpression))


@dataclass
class ObjectExactCardinality(FunOwlBase):
    card: NonNegativeInteger
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: Optional["ClassExpression"]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.card + self.objectPropertyExpression).opt(self.classExpression))


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
        return w.func(self, lambda: (w + self.dataPropertyExpression + self.dataRanged))


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
    dataRange: Optional[DataRange]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.min_ + self.dataPropertyExpression).opt(self.dataRange))


@dataclass
class DataMaxCardinality(FunOwlBase):
    max_: NonNegativeInteger
    dataPropertyExpression: DataPropertyExpression
    dataRange: Optional[DataRange]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.max_ + self.dataPropertyExpression).opt(self.dataRange))


@dataclass
class DataExactCardinality(FunOwlBase):
    card: NonNegativeInteger
    dataPropertyExpression: DataPropertyExpression
    dataRange: Optional[DataRange]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.exprs, 'exprs', 2)
        return w.func(self, lambda: (w + self.card + self.dataPropertyExpression).opt(self.dataRange))


# A Class expression can be a class or any subclass of ClassExpression
# @dataclass
# class ClassExpression(FunOwlBase):
ClassExpression = Union[Class, ObjectIntersectionOf, ObjectUnionOf, ObjectComplementOf, ObjectOneOf,
    ObjectSomeValuesFrom, ObjectAllValuesFrom, ObjectHasValue, ObjectHasSelf,
    ObjectMinCardinality, ObjectMaxCardinality, ObjectExactCardinality,
    DataSomeValuesFrom, DataAllValuesFrom, DataHasValue,
    DataMinCardinality, DataMaxCardinality, DataExactCardinality]
