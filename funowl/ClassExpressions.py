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
from typing import List, Union

from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.writers import FunctionalWriter
from funowl.DataRanges import DataRange
from funowl.Declarations import ObjectPropertyExpression, DataPropertyExpression, Class
from funowl.base.fun_owl_base import FunOwlBase
from funowl.GeneralDefinitions import NonNegativeInteger
from funowl.Individuals import Individual
from funowl.Literals import Literal


# A Class expression can be a class or any subclass of ClassExpression_
class ClassExpression_(FunOwlBase):
    pass


@dataclass
class ClassExpression(FunOwlChoice):
    v: Union[Class, ClassExpression_]
    coercion_allowed = False            # Have to be explicitly declared


class ObjectIntersectionOf(ClassExpression_):
    classExpressions: List[ClassExpression]

    def __init__(self, *classExpressions: ClassExpression) -> None:
        self.classExpressions = list(classExpressions)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.classExpressions, 'exprs', 2)
        return w.func(self, lambda: w.iter(self.classExpressions))


class ObjectUnionOf(ClassExpression_):
    classExpressions: List[ClassExpression]

    def __init__(self, *classExpressions: ClassExpression) -> None:
        self.classExpressions = list(classExpressions)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.classExpressions, 'exprs', 2)
        return w.func(self, lambda: w.iter(self.classExpressions))


class ObjectComplementOf(ClassExpression_):
    classExpression: ClassExpression

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.classExpression)


class ObjectOneOf(ClassExpression_):
    individuals: List[Individual]

    def __init__(self, *individuals: Individual) -> None:
        self.individuals = list(individuals)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.exprs, 'exprs', 2)
        return w.func(self, lambda: w.iter(self.individuals))


@dataclass
class ObjectSomeValuesFrom(ClassExpression_):
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: ClassExpression

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.exprs, 'exprs', 2)
        return w.func(self, lambda: w + self.objectPropertyExpression + self.classExpression)


@dataclass
class ObjectAllValuesFrom(ClassExpression_):
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: ClassExpression

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.exprs, 'exprs', 2)
        return w.func(self, lambda: w + self.objectPropertyExpression + self.classExpression)


@dataclass
class ObjectHasValue(ClassExpression_):
    objectPropertyExpression: ObjectPropertyExpression
    individual: Individual

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.exprs, 'exprs', 2)
        return w.func(self, lambda: w + self.objectPropertyExpression + self.individual)


@dataclass
class ObjectHasSelf(ClassExpression_):
    objectPropertyExpression: ObjectPropertyExpression

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.exprs, 'exprs', 2)
        return w.func(self, lambda: w + self.objectPropertyExpression)


@dataclass
class ObjectMinCardinality(ClassExpression_):
    min_: NonNegativeInteger
    objectPropertyExpression: ObjectPropertyExpression
    classExpressions: List[ClassExpression]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.exprs, 'exprs', 2)
        return w.func(self, lambda: (w + self.min_ + self.objectPropertyExpression).iter(self.classExpressions))


@dataclass
class ObjectMaxCardinality(ClassExpression_):
    max_: NonNegativeInteger
    objectPropertyExpression: ObjectPropertyExpression
    classExpressions: List[ClassExpression]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.exprs, 'exprs', 2)
        return w.func(self, lambda: (w + self.max_ + self.objectPropertyExpression).iter(self.classExpressions))


@dataclass
class ObjectExactCardinality(ClassExpression_):
    card: NonNegativeInteger
    objectPropertyExpression: ObjectPropertyExpression
    classExpressions: List[ClassExpression]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.exprs, 'exprs', 2)
        return w.func(self, lambda: (w + self.card + self.objectPropertyExpression).iter(self.classExpressions))


@dataclass
class DataSomeValuesFrom(ClassExpression_):
    dataPropertyExpression: DataPropertyExpression
    dataRange: DataRange

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.exprs, 'exprs', 2)
        return w.func(self, lambda: (w + self.dataPropertyExpression + self.dataRanged))


@dataclass
class DataAllValuesFrom(ClassExpression_):
    dataPropertyExpression: DataPropertyExpression
    dataRange: DataRange

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.exprs, 'exprs', 2)
        return w.func(self, lambda: (w + self.dataPropertyExpression + self.dataRanged))


@dataclass
class DataHasValue(ClassExpression_):
    dataPropertyExpression: DataPropertyExpression
    literal: Literal

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.exprs, 'exprs', 2)
        return w.func(self, lambda: (w + self.dataPropertyExpression + self.literal))


@dataclass
class DataMinCardinality(ClassExpression_):
    min_: NonNegativeInteger
    dataPropertyExpression: DataPropertyExpression
    dataRange: List[DataRange]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.exprs, 'exprs', 2)
        return w.func(self, lambda: (w + self.min_ + self.dataPropertyExpression).iter(self.dataRange))


@dataclass
class DataMaxCardinality(ClassExpression_):
    max_: NonNegativeInteger
    dataPropertyExpression: DataPropertyExpression
    dataRange: List[DataRange]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.exprs, 'exprs', 2)
        return w.func(self, lambda: (w + self.max_ + self.dataPropertyExpression).iter(self.dataRange))


@dataclass
class DataExactCardinality(ClassExpression_):
    card: NonNegativeInteger
    dataPropertyExpression: DataPropertyExpression
    dataRange: List[DataRange]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.exprs, 'exprs', 2)
        return w.func(self, lambda: (w + self.card + self.dataPropertyExpression).iter(self.dataRange))
