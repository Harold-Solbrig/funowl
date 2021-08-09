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
from typing import List, ClassVar, Union, Optional, ForwardRef

from rdflib import URIRef, OWL, Graph, RDF
from rdflib.term import BNode, Literal as RDFLiteral

from funowl.base.fun_owl_base import FunOwlBase
from funowl.base.list_support import ListWrapper
from funowl.base.rdftriple import SUBJ
from funowl.converters.rdf_converter import SEQ
from funowl.dataproperty_expressions import DataPropertyExpression
from funowl.dataranges import DataRange
from funowl.general_definitions import NonNegativeInteger
from funowl.identifiers import IRI
from funowl.individuals import Individual
from funowl.literals import Literal
from funowl.objectproperty_expressions import ObjectPropertyExpression
# TODO: find out why we can't import this and/or why the types that are currently wrapped in ForwardRef below don't
#       work if they are plain strings.  Maybe we need 3.8?
from funowl.terminals.TypingHelper import proc_forwards
from funowl.writers import FunctionalWriter


class Class(IRI):
    v: IRI.types() = IRI.v_field()
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

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # _:x rdf:type owl:Class .
        # _:x owl:intersectionOf T(SEQ CE1 ... CEn) .
        subj = BNode()
        g.add((subj, RDF.type, OWL.Class))
        g.add((subj, OWL.intersectionOf, SEQ(g, self.classExpressions)))
        return subj

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return []       # There are no subjects in object intersection -- only objects

@dataclass
class ObjectUnionOf(FunOwlBase):
    classExpressions: List["ClassExpression"]

    def __init__(self, *classExpression: "ClassExpression") -> None:
        self.classExpressions = ListWrapper(classExpression, ClassExpression)
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        self.list_cardinality(self.classExpressions, 'exprs', 2)
        return w.func(self, lambda: w.iter(self.classExpressions))

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # _:x rdf:type owl:Class .
        # _:x owl:unionOf T(SEQ CE1 ... CEn) .
        x = BNode()
        g.add((x, RDF.type, OWL.Class))
        g.add((x, OWL.unionOf, SEQ(g, self.classExpressions)))
        return x

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return []       # There are no subjects in object union -- only objects

@dataclass
class ObjectComplementOf(FunOwlBase):
    classExpression:ForwardRef("ClassExpression")

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.classExpression)

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # _:x rdf:type owl:Class .
        # _:x owl:complementOf T(CE) .
        x = BNode()
        g.add((x, RDF.type, OWL.Class))
        g.add((x, OWL.complementOf, self.classExpression.to_rdf(g)))
        return x

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return []       # There are no subjects in object comlement -- only objects

@dataclass(init=False)
class ObjectOneOf(FunOwlBase):
    individuals: List[Individual.types()]

    def __init__(self, *individual: Individual) -> None:
        self.individuals = list(individual)
        super().__init__()

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w.iter(self.individuals))

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # _:x rdf:type owl:Class .
        # _:x owl:oneOf T(SEQ a1 ... an) .
        x = BNode()
        g.add((x, RDF.type, OWL.Class))
        g.add((x, OWL.oneOf, SEQ(g, self.individuals)))
        return x

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return []       # There are no subjects in object one of -- only objects

@dataclass
class ObjectSomeValuesFrom(FunOwlBase):
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: ForwardRef("ClassExpression")
    coercion_allowed: ClassVar[bool] = True

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.objectPropertyExpression + self.classExpression)

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # _:x rdf:type owl:Restriction .
        # _:x owl:onProperty T(OPE) .
        # _:x owl:someValuesFrom T(CE) .
        x = BNode()
        g.add((x, RDF.type, OWL.Restriction))
        g.add((x, OWL.onProperty, self.objectPropertyExpression.to_rdf(g)))
        g.add((x, OWL.someValuesFrom, self.classExpression.to_rdf(g)))
        return x

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return []       # There are no subjects in object some values from -- only objects

@dataclass
class ObjectAllValuesFrom(FunOwlBase):
    objectPropertyExpression: ObjectPropertyExpression
    classExpression:ForwardRef("ClassExpression")

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.objectPropertyExpression + self.classExpression)

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # _:x rdf:type owl:Restriction .
        # _:x owl:onProperty T(OPE) .
        # _:x owl:allValuesFrom T(CE) .
        x = BNode()
        g.add((x, RDF.type, OWL.Restriction))
        g.add((x, OWL.onProperty, self.objectPropertyExpression.to_rdf(g)))
        g.add((x, OWL.allValuesFrom, self.classExpression.to_rdf(g)))
        return x

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return []               # Universal quantifiers don't have a subject


@dataclass
class ObjectHasValue(FunOwlBase):
    objectPropertyExpression: ObjectPropertyExpression
    individual: Individual

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.objectPropertyExpression + self.individual)

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # _:x rdf:type owl:Restriction .
        # _:x owl:onProperty T(OPE) .
        # _:x owl:hasValue T(a) .
        x = BNode()
        g.add((x, RDF.type, OWL.Restriction))
        g.add((x, OWL.onProperty, self.objectPropertyExpression.to_rdf(g)))
        g.add((x, OWL.hasValue, self.individual.to_rdf(g)))
        return x

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return self.objectPropertyExpression._subjects(g)

@dataclass
class ObjectHasSelf(FunOwlBase):
    objectPropertyExpression: ObjectPropertyExpression

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w + self.objectPropertyExpression)

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # _:x rdf:type owl:Restriction .
        # _:x owl:onProperty T(OPE) .
        # _:x owl:hasSelf "true"^^xsd:boolean .
        x = BNode()
        g.add((x, RDF.type, OWL.Restriction))
        g.add((x, OWL.onProperty, self.objectPropertyExpression.to_rdf(g)))
        g.add((x, OWL.hasSelf, RDFLiteral(True)))
        return x

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return self.objectPropertyExpression._subjects(g)

@dataclass
class ObjectMinCardinality(FunOwlBase):
    min_: NonNegativeInteger
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: Optional["ClassExpression"] = None

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.min_ + self.objectPropertyExpression).opt(self.classExpression))

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # _:x rdf:type owl:Restriction .
        # _:x owl:onProperty T(OPE) .
        # _:x owl:minCardinality "n"^^xsd:nonNegativeInteger .
        #
        # _:x owl:minQualifiedCardinality "n"^^xsd:nonNegativeInteger .
        # _:x owl:onClass T(CE) .
        x = BNode()
        g.add((x, RDF.type, OWL.Restriction))
        g.add((x, OWL.onProperty, self.objectPropertyExpression.to_rdf(g)))
        if self.classExpression:
            g.add((x, OWL.minQualifiedCardinality, self.min_.to_rdf(g)))
            g.add((x, OWL.onClass, self.classExpression.to_rdf(g)))
        else:
            g.add((x, OWL.minCardinality, self.min_.to_rdf(g)))
        return x

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return self.objectPropertyExpression._subjects(g)


@dataclass
class ObjectMaxCardinality(FunOwlBase):
    max_: NonNegativeInteger
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: Optional["ClassExpression"] = None

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.max_ + self.objectPropertyExpression).opt(self.classExpression))

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # _:x rdf:type owl:Restriction .
        # _:x owl:onProperty T(OPE) .
        # _:x owl:maxCardinality "n"^^xsd:nonNegativeInteger .
        #
        # _:x owl:maxQualifiedCardinality "n"^^xsd:nonNegativeInteger .
        # _:x owl:onClass T(CE) .
        x = BNode()
        g.add((x, RDF.type, OWL.Restriction))
        g.add((x, OWL.onProperty, self.objectPropertyExpression.to_rdf(g)))
        if self.classExpression:
            g.add((x, OWL.maxQualifiedCardinality, self.max_.to_rdf(g)))
            g.add((x, OWL.onClass, self.classExpression.to_rdf(g)))
        else:
            g.add((x, OWL.maxCardinality, self.max_.to_rdf(g)))
        return x

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return self.objectPropertyExpression._subjects(g)

@dataclass
class ObjectExactCardinality(FunOwlBase):
    card: NonNegativeInteger
    objectPropertyExpression: ObjectPropertyExpression
    classExpression: Optional["ClassExpression"] = None

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.card + self.objectPropertyExpression).opt(self.classExpression))

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # _:x rdf:type owl:Restriction .
        # _:x owl:onProperty T(OPE) .
        # _:x owl:cardinality "n"^^xsd:nonNegativeInteger .
        #     or
        # _:x owl:qualifiedCardinality "n"^^xsd:nonNegativeInteger .
        # _:x owl:onClass T(CE) .
        x = BNode()
        g.add((x, RDF.type, OWL.Restriction))
        g.add((x, OWL.onProperty, self.objectPropertyExpression.to_rdf(g)))
        if self.classExpression:
            g.add((x, OWL.qualifiedCardinality, self.card.to_rdf(g)))
            g.add((x, OWL.onClass, self.classExpression.to_rdf(g)))
        else:

            g.add((x, OWL.cardinality, self.card.to_rdf(g)))
        return x

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return self.objectPropertyExpression._subjects(g)

@dataclass
class DataSomeValuesFrom(FunOwlBase):
    dataPropertyExpressions: List[DataPropertyExpression]
    dataRange: DataRange

    def __init__(self, *dataPropertyExpressions: Union[DataPropertyExpression, DataRange]) -> None:
        self.dataPropertyExpressions = list(dataPropertyExpressions[:-1])
        self.dataRange = dataPropertyExpressions[-1]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w.iter(self.dataPropertyExpressions) + self.dataRange)

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # N == 1
        #    _:x rdf:type owl:Restriction .
        #   _:x owl:onProperty T(DPE) .
        #    _:x owl:someValuesFrom T(DR) .
        # N >= 2
        #    _:x rdf:type owl:Restriction .
        #    _:x owl:onProperties T(SEQ DPE1 ... DPEn) .
        #    _:x owl:someValuesFrom T(DR) .
        subj = BNode()
        g.add((subj, RDF.type, OWL.Restriction))
        if len(self.dataPropertyExpressions) >= 2:
            g.add((subj, OWL.onProperties, SEQ(g, self.dataPropertyExpressions)))
        else:
            g.add((subj, OWL.onProperty, self.dataPropertyExpressions[0].to_rdf(g)))
        g.add((subj, OWL.someValuesFrom, self.dataRange.to_rdf(g)))
        return subj

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return []           # No subjects for this construct


@dataclass
class DataAllValuesFrom(FunOwlBase):
    dataPropertyExpressions: List[DataPropertyExpression]
    dataRange: DataRange

    def __init__(self, *dataPropertyExpressions: Union[DataPropertyExpression, DataRange]) -> None:
        self.dataPropertyExpressions = list(dataPropertyExpressions[:-1])
        self.dataRange = dataPropertyExpressions[-1]

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w.iter(self.dataPropertyExpressions) + self.dataRange)

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # N == 1
        #    _:x rdf:type owl:Restriction .
        #   _:x owl:onProperty T(DPE) .
        #    _:x owl:allValuesFrom T(DR) .
        # N >= 2
        #    _:x rdf:type owl:Restriction .
        #    _:x owl:onProperties T(SEQ DPE1 ... DPEn) .
        #    _:x owl:allValuesFrom T(DR) .
        subj = BNode()
        g.add((subj, RDF.type, OWL.Restriction))
        if len(self.dataPropertyExpressions) >= 2:
            g.add((subj, OWL.onProperties, SEQ(g, self.dataPropertyExpressions)))
        else:
            g.add((subj, OWL.onProperty, self.dataPropertyExpressions[0].to_rdf(g)))
        g.add((subj, OWL.allValuesFrom, self.dataRange.to_rdf(g)))
        return subj

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return []           # No subjects for this construct


@dataclass
class DataHasValue(FunOwlBase):
    dataPropertyExpression: DataPropertyExpression
    literal: Literal

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.dataPropertyExpression + self.literal))

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # _:x rdf:type owl:Restriction .
        # _:x owl:onProperty T(DPE) .
        # _:x owl:hasValue T(lt) .
        x = BNode()
        g.add((x, RDF.type, OWL.Restriction))
        g.add((x, OWL.onProperty, self.dataPropertyExpression.to_rdf(g)))
        g.add((x, OWL.hasValue, self.literal.to_rdf(g)))
        return x

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return self.dataPropertyExpression._subjects(g)

@dataclass
class DataMinCardinality(FunOwlBase):
    min_: NonNegativeInteger
    dataPropertyExpression: DataPropertyExpression
    dataRange: Optional[DataRange] = None

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.min_ + self.dataPropertyExpression).opt(self.dataRange))

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        #  _:x rdf:type owl:Restriction .
        # _:x owl:onProperty T(DPE) .
        # _:x owl:minCardinality "n"^^xsd:nonNegativeInteger
        #
        # _:x owl:minQualifiedCardinality "n"^^xsd:nonNegativeInteger .
        # _:x owl:onDataRange T(DR) .
        x = BNode()
        g.add((x, RDF.type, OWL.Restriction))
        g.add((x, OWL.onProperty, self.dataPropertyExpression.to_rdf(g)))
        if self.dataRange:
            g.add((x, OWL.minQualifiedCardinality, self.min_.to_rdf(g)))
            g.add((x, OWL.onDataRange, self.dataRange.to_rdf(g)))
        else:
            g.add((x, OWL.minCardinality, self.min_.to_rdf(g)))
        return x

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return self.dataPropertyExpression._subjects(g)


@dataclass
class DataMaxCardinality(FunOwlBase):
    max_: NonNegativeInteger
    dataPropertyExpression: DataPropertyExpression
    dataRange: Optional[DataRange] = None

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.max_ + self.dataPropertyExpression).opt(self.dataRange))

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # _:x rdf:type owl:Restriction .
        # _:x owl:onProperty T(DPE) .
        # _:x owl:maxCardinality "n"^^xsd:nonNegativeInteger .
        #
        # _:x owl:maxQualifiedCardinality "n"^^xsd:nonNegativeInteger .
        # _:x owl:onDataRange T(DR) .
        x = BNode()
        g.add((x, RDF.type, OWL.Restriction))
        g.add((x, OWL.onProperty, self.dataPropertyExpression.to_rdf(g)))
        if self.dataRange:
            g.add((x, OWL.maxQualifiedCardinality, self.max_.to_rdf(g)))
            g.add((x, OWL.onDataRange, self.dataRange.to_rdf(g)))
        else:
            g.add((x, OWL.maxCardinality, self.max_.to_rdf(g)))
        return x

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return self.dataPropertyExpression._subjects(g)

@dataclass
class DataExactCardinality(FunOwlBase):
    card: NonNegativeInteger
    dataPropertyExpression: DataPropertyExpression
    dataRange: Optional[DataRange] = None

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.card + self.dataPropertyExpression).opt(self.dataRange))

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
        # _:x rdf:type owl:Restriction .
        # _:x owl:onProperty T(DPE) .
        # _:x owl:cardinality "n"^^xsd:nonNegativeInteger .
        #
        # _:x owl:qualifiedCardinality "n"^^xsd:nonNegativeInteger .
        # _:x owl:onDataRange T(DR) .
        x = BNode()
        g.add((x, RDF.type, OWL.Restriction))
        g.add((x, OWL.onProperty, self.dataPropertyExpression.to_rdf(g)))
        if self.dataRange:
            g.add((x, OWL.qualifiedCardinality, self.card.to_rdf(g)))
            g.add((x, OWL.onDataRange, self.dataRange.to_rdf(g)))
        else:
            g.add((x, OWL.cardinality, self.card.to_rdf(g)))
        return x

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return self.dataPropertyExpression._subjects(g)


# A Class expression can be a class or any subclass of ClassExpression
# @dataclass
# class ClassExpression(FunOwlBase):
ClassExpression = Union[Class, ObjectIntersectionOf, ObjectUnionOf, ObjectComplementOf, ObjectOneOf,
    ObjectSomeValuesFrom, ObjectAllValuesFrom, ObjectHasValue, ObjectHasSelf,
    ObjectMinCardinality, ObjectMaxCardinality, ObjectExactCardinality,
    DataSomeValuesFrom, DataAllValuesFrom, DataHasValue,
    DataMinCardinality, DataMaxCardinality, DataExactCardinality]

proc_forwards(ObjectMinCardinality, globals())
proc_forwards(ObjectMaxCardinality, globals())
proc_forwards(ObjectExactCardinality, globals())
proc_forwards(ObjectIntersectionOf, globals())
proc_forwards(ObjectUnionOf, globals())
proc_forwards(ObjectComplementOf, globals())
proc_forwards(ObjectSomeValuesFrom, globals())
proc_forwards(ObjectAllValuesFrom, globals())
