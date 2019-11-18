from rdflib import Namespace, Literal, XSD

from funowl import Ontology, ObjectProperty, DataProperty, Class, ObjectOneOf, DifferentIndividuals, \
    NamedIndividual, ObjectPropertyAssertion, DataPropertyAssertion, OntologyDocument, ClassAssertion

EX = Namespace("http://example.org/test#")
SP = Namespace("http://nlm.org/singleton#")
WK = Namespace("http://example.org/wk#")

o = Ontology(EX.singletonPropertyOriginal)


o.axioms.append(ObjectPropertyAssertion(EX.isMarriedTo1, EX.BobDylan, EX.SaraLownds))
o.axioms.append(ObjectPropertyAssertion(EX.isMarriedTo2, EX.BobDylan, EX.CarolDennis))
o.axioms.append(ObjectPropertyAssertion(EX.isMarriedTo1, SP.singletonPropertyOf, EX.isMarriedTo))
o.axioms.append(ObjectPropertyAssertion(EX.isMarriedTo2, SP.singletonPropertyOf, EX.isMarriedTo))
o.axioms.append(ObjectPropertyAssertion(EX.isMarriedTo1, EX.hasSource, WK.Bob_Dylan))
o.axioms.append(ObjectPropertyAssertion(EX.isMarriedTo2, EX.hasSource, WK.Sara_Dylan))
o.axioms.append(DataPropertyAssertion(EX.isMarriedTo1, EX.extractedOn, Literal("2009-06-07T00:00:00", datatype=XSD.dateTime)))
o.axioms.append(DataPropertyAssertion(EX.isMarriedTo1, EX.extractedOn, Literal("2009-08-08T00:00:00", datatype=XSD.dateTime)))

doc = OntologyDocument(EX, sp=SP, ontology=o)
print(str(doc.to_functional()))