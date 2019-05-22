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

from funowl.Declarations import ObjectPropertyExpression, DataPropertyExpression, Class
from funowl.FunOwlBase import FunOwlBase, FunOwlChoice
from funowl.GeneralDefinitions import NonNegativeInteger
from funowl.Individuals import Individual


@dataclass
class ClassExpression(FunOwlChoice):
    v: Union[Class, "ClassExpression_"]


class ClassExpression_(FunOwlBase):
    pass


class ObjectIntersectionOf(ClassExpression_):
    exprs: List[ClassExpression]

    def __init__(self, *exprs: ClassExpression) -> None:
        self.exprs = list(exprs)

    def as_owl(self, indent: int = 0) -> str:
        return self.list_cardinality(self.exprs, "exprs", 2).\
            func_name(indent, lambda i1: self.iter(i1, self.exprs))


class ObjectUnionOf(ClassExpression_):
    exprs: List[ClassExpression]

    def __init__(self, *exprs: ClassExpression) -> None:
        self.exprs = list(exprs)

    def as_owl(self, indent: int = 0) -> str:
        return self.list_cardinality(self.exprs, "exprs", 2).\
            func_name(indent, lambda i1: self.iter(i1, self.exprs))


class ObjectComplementOf(ClassExpression_):
    expr: ClassExpression

    def as_owl(self, indent: int = 0) -> str:
        return self.func_name(indent, lambda i1: self.expr.as_owl(i1))


class ObjectOneOf(ClassExpression_):
    individuals: List[Individual]

    def __init__(self, *individuals: Individual) -> None:
        self.individuals = list(individuals)

    def as_owl(self, indent: int = 0) -> str:
        return self.list_cardinality(self.individuals, "individuals", 2).\
            func_name(indent, lambda i1: self.iter(i1, self.individuals))

@dataclass
class ObjectSomeValuesFrom(ClassExpression_):
    propertyExpression: ObjectPropertyExpression
    classExpression: ClassExpression

    def as_owl(self, indent: int = 0) -> str:
        return self.func_name(indent,
                              lambda i1: self.propertyExpression.as_owl(i1) + ' ' + self.classExpression.as_owl(i1))


@dataclass
class ObjectAllValuesFrom(ClassExpression_):
    propertyExpression: ObjectPropertyExpression
    classExpression: ClassExpression

    def as_owl(self, indent: int = 0) -> str:
        return self.func_name(indent,
                              lambda i1: self.propertyExpression.as_owl(i1) + ' ' + self.classExpression.as_owl(i1))

@dataclass
class ObjectHasValue(ClassExpression_):
    propertyExpression: ObjectPropertyExpression
    individual: Individual

    def as_owl(self, indent: int = 0) -> str:
        return self.func_name(indent,
                              lambda i1: self.propertyExpression.as_owl(i1) + ' ' + self.individual.as_owl(i1))

@dataclass
class ObjectHasSelf(ClassExpression_):
    propertyExpression: ObjectPropertyExpression

    def as_owl(self, indent: int = 0) -> str:
        return self.func_name(indent, lambda i1: self.propertyExpression.as_owl(i1))


@dataclass
class ObjectMinCardinality(ClassExpression_):
    min_ : NonNegativeInteger
    propertyExpression: ObjectPropertyExpression
    classExpressions: List[ClassExpression]

    def as_owl(self, indent: int = 0) -> str:
        return self.func_name(indent,
                              lambda i1: str(self.min_) + self.propertyExpression.as_owl(i1) +
                                         self.iter(i1, self.classExpressions))


@dataclass
class ObjectMaxCardinality(ClassExpression_):
    max_ : NonNegativeInteger
    propertyExpression: ObjectPropertyExpression
    classExpressions: List[ClassExpression]

    def as_owl(self, indent: int = 0) -> str:
        return self.func_name(indent,
                              lambda i1: str(self.max_) + self.propertyExpression.as_owl(i1) +
                                         self.iter(i1, self.classExpressions))


@dataclass
class ObjectExactCardinality(ClassExpression_):
    card : NonNegativeInteger
    propertyExpression: ObjectPropertyExpression
    classExpressions: List[ClassExpression]

    def as_owl(self, indent: int = 0) -> str:
        return self.func_name(indent,
                              lambda i1: str(self.card) + self.propertyExpression.as_owl(i1) +
                                         self.iter(i1, self.classExpressions))


@dataclass
class DataSomeValuesFrom(ClassExpression_):
    propertyExpression: DataPropertyExpression
    classExpression: ClassExpression

    def as_owl(self, indent: int = 0) -> str:
        return self.func_name(indent,
                              lambda i1: self.propertyExpression.as_owl(i1) + self.classExpression.as_owl(i1))


@dataclass
class DataAllValuesFrom(ClassExpression_):
    propertyExpression: DataPropertyExpression
    classExpression: ClassExpression

    def as_owl(self, indent: int = 0) -> str:
        return self.func_name(indent,
                              lambda i1: self.propertyExpression.as_owl(i1) + self.classExpression.as_owl(i1))


@dataclass
class DataHasValue(ClassExpression_):
    propertyExpression: DataPropertyExpression
    individual: Individual

    def as_owl(self, indent: int = 0) -> str:
        return self.func_name(indent,
                              lambda i1: self.propertyExpression.as_owl(i1) + self.individual.as_owl(i1))

@dataclass
class DataMinCardinality(ClassExpression_):
    min_: NonNegativeInteger
    propertyExpression: DataPropertyExpression
    classExpressions: List[ClassExpression]

    def as_owl(self, indent: int = 0) -> str:
        return self.func_name(indent,
                              lambda i1: str(self.min_) + self.propertyExpression.as_owl(i1) +
                                         self.iter(i1, self.classExpressions))


@dataclass
class DataMaxCardinality(ClassExpression_):
    max_: NonNegativeInteger
    propertyExpression: DataPropertyExpression
    classExpressions: List[ClassExpression]

    def as_owl(self, indent: int = 0) -> str:
        return self.func_name(indent,
                              lambda i1: str(self.max_) + self.propertyExpression.as_owl(i1) +
                                         self.iter(i1, self.classExpressions))


@dataclass
class DataExactCardinality(ClassExpression_):
    card: NonNegativeInteger
    propertyExpression: DataPropertyExpression
    classExpressions: List[ClassExpression]

    def as_owl(self, indent: int = 0) -> str:
        return self.func_name(indent,
                              lambda i1: str(self.card) + self.propertyExpression.as_owl(i1) +
                                         self.iter(i1, self.classExpressions))


@dataclass
class HasKey(FunOwlBase):
    classexpr: ClassExpression
    objectPropertyExprs: List[ObjectPropertyExpression]
    dataPropertyExprs: List[DataPropertyExpression]

    def as_owl(self, indent: int = 0) -> str:
        return self.func_name(indent,
                              lambda i1: self.classexpr.as_owl(i1) +
                                         '(' + self.iter(i1, self.objectPropertyExprs) + ')' +
                                         '(' + self.iter(i1, self.dataPropertyExprs) + ')')


