from rdflib import Namespace, Literal, XSD

from funowl import Ontology, ObjectProperty, DataProperty, Class, ObjectOneOf, DifferentIndividuals, \
    NamedIndividual, ObjectPropertyAssertion, DataPropertyAssertion, OntologyDocument, ClassAssertion

EX = Namespace("http://example.org/test#")
SP = Namespace("http://nlm.org/singleton#")

o = Ontology(EX.singletonText)

# General setup for singleton model
# NOTE 1: SingletonProperty is NOT in the RDF namespace
o.declaration(Class(SP.SingletonProperty))
o.declaration(ObjectProperty(SP.SingletonProperty))
o.axioms.append(ClassAssertion(SP.singletonProperty, SP.SingletonProperty))

# Specific example
o.declaration(DataProperty(EX.hasStart))
o.declaration(DataProperty(EX.hasEnd))
o.declaration(ObjectProperty(EX.isMarriedTo))
o.declaration(ObjectProperty(EX.isMarriedTo1))
o.declaration(ObjectProperty(EX.isMarriedTo2))
o.subClassOf(ObjectOneOf(EX.isMarriedTo1, EX.isMarriedTo2), EX.isMarriedTo)
o.axioms.append(DifferentIndividuals(EX.isMarriedTo1, EX.isMarriedTo2))

o.declaration(NamedIndividual(EX.BobDylan))
o.declaration(NamedIndividual(EX.SaraLownds))
o.declaration(NamedIndividual(EX.CarolDennis))

o.axioms.append(ObjectPropertyAssertion(EX.isMarriedTo1, EX.BobDylan, EX.SaraLownds))
o.axioms.append(ObjectPropertyAssertion(EX.isMarriedTo2, EX.BobDylan, EX.CarolDennis))

o.axioms.append(DataPropertyAssertion(EX.hasStart,  EX.isMarriedTo1, Literal("1986-01-03T00:00:00", datatype=XSD.dateTime)))
o.axioms.append(DataPropertyAssertion(EX.hasEnd,  EX.isMarriedTo1, Literal("1992-10-01T00:00:00", datatype=XSD.dateTime)))

doc = OntologyDocument(EX, sp=SP, ontology=o)
print(str(doc.to_functional()))


