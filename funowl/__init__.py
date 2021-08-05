import sys
from warnings import warn

from . prefix_declarations import Prefix
from . declarations import Declaration
from . literals import Datatype, StringLiteralNoLanguage, TypedLiteral, StringLiteralWithLanguage, Literal
from . dataproperty_expressions import DataProperty
from . individuals import NamedIndividual
from . annotations import AnnotationProperty, AnnotationSubject, AnnotationValue, Annotation, Annotatable, \
    AnnotationAssertion, SubAnnotationPropertyOf, AnnotationPropertyDomain, AnnotationPropertyRange, AnnotationAxiom
from . assertions import SameIndividual, DifferentIndividuals, ClassAssertion, ObjectPropertyExpression, \
    ObjectPropertyAssertion, NegativeObjectPropertyAssertion, DataPropertyAssertion, NegativeDataPropertyAssertion, \
    Assertion
from . class_axioms import SubClassOf, EquivalentClasses, DisjointClasses, DisjointUnion, HasKey, ClassAxiom
from . class_expressions import Class, ObjectIntersectionOf, ObjectUnionOf, ObjectComplementOf, ObjectOneOf, \
    ObjectSomeValuesFrom, ObjectAllValuesFrom, ObjectHasValue, ObjectHasSelf, ObjectMinCardinality, \
    ObjectMaxCardinality, ObjectExactCardinality, DataSomeValuesFrom, DataAllValuesFrom, DataHasValue, \
    DataMinCardinality, DataMaxCardinality, DataExactCardinality, ClassExpression
from . dataproperty_axioms import SubDataPropertyOf, EquivalentDataProperties, DisjointDataProperties, \
    DataPropertyDomain, DataPropertyRange, FunctionalDataProperty, DatatypeDefinition, DataPropertyAxiom
from . dataproperty_expressions import DataProperty, DataPropertyExpression
from . dataranges import DataIntersectionOf, DataUnionOf, DataComplementOf, DataOneOf, FacetRestriction, \
    DatatypeRestriction, DataRange
from .identifiers import IRI
from . individuals import NamedIndividual, AnonymousIndividual, Individual
from . objectproperty_axioms import ObjectPropertyChain, SubObjectPropertyExpression, SubObjectPropertyOf,\
    EquivalentObjectProperties, DisjointObjectProperties, ObjectPropertyDomain, ObjectPropertyRange, \
    InverseObjectProperties, FunctionalObjectProperty, InverseFunctionalObjectProperty, ReflexiveObjectProperty, \
    IrreflexiveObjectProperty, SymmetricObjectProperty, AsymmetricObjectProperty, TransitiveObjectProperty, \
    ObjectPropertyAxiom
from . objectproperty_expressions import ObjectProperty, ObjectInverseOf, ObjectPropertyExpression
from . ontology_document import OntologyDocument, Ontology, Import
from . axioms import Axiom


if sys.version_info < (3, 8, 0):
    warn(f"FunOwl needs python 3.8 or later.  Current version: {sys.version_info}")

# TODO: Run coverage and test or toss anything that isn't executed
# TODO: Consider removing the streaming IO feature -- it doesn't seem to do a lot for performance and makes things compicated
# TODO: Put an official unit test in -- something like rdflib
# TODO: See table 5 in OWL Spec -- builtin solution?
