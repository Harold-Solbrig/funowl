from . prefix_declarations import Prefix
from . ontology_document import OntologyDocument, Ontology, Import
from . declarations import Declaration, Class, Datatype, ObjectProperty, DataProperty, AnnotationProperty, \
    NamedIndividual
from . annotations import Annotation, AnnotationAssertion, SubAnnotationPropertyOf, AnnotationPropertyDomain, \
    AnnotationPropertyRange
from . objectproperty_expressions import ObjectInverseOf
from . dataranges import DataIntersectionOf, DataUnionOf, DataComplementOf, DataOneOf, DatatypeRestriction
from . class_expressions import ObjectIntersectionOf, ObjectUnionOf, ObjectComplementOf, ObjectOneOf, \
    ObjectSomeValuesFrom, ObjectAllValuesFrom, ObjectHasValue, ObjectHasSelf, ObjectMinCardinality, \
    ObjectMaxCardinality, ObjectExactCardinality, DataSomeValuesFrom, DataAllValuesFrom, DataHasValue, \
    DataMinCardinality, DataMaxCardinality, DataExactCardinality
from . class_axioms import SubClassOf, EquivalentClasses, DisjointClasses, DisjointUnion, HasKey
from . objectproperty_axioms import SubObjectPropertyOf, ObjectPropertyChain, EquivalentObjectProperties, \
    DisjointObjectProperties, ObjectPropertyDomain, ObjectPropertyRange, InverseObjectProperties, \
    FunctionalObjectProperty, InverseFunctionalObjectProperty, ReflexiveObjectProperty, IrreflexiveObjectProperty, \
    SymmetricObjectProperty, AsymmetricObjectProperty, TransitiveObjectProperty
from . dataproperty_axioms import SubDataPropertyOf, EquivalentDataProperties, DisjointDataProperties, \
    DataPropertyDomain, DataPropertyRange, FunctionalDataProperty, DatatypeDefinition
from . assertions import SameIndividual, DifferentIndividuals, ClassAssertion, ObjectPropertyAssertion, \
    NegativeObjectPropertyAssertion, DataPropertyAssertion, NegativeDataPropertyAssertion

