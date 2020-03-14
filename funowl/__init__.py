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

# TODO: Run coverage and toss anything that isn't executed
# TODO: Look for NON-Dataclass elements, noting that the "fields" function is dataclass only
# TODO: Look at the _coericion_allowed variable and see whether it can't be removed
# TODO: Consider removing the streaming IO feature -- it doesn't seem to do a lot for performance and makes things compicated
# TODO: Look at all disabled unit tests
# TODO: Put an official unit test in -- something like rdflib