import unittest


class MyTestCase(unittest.TestCase):
    def test_readme_example1(self):
        from rdflib import RDFS, OWL, Namespace
        from funowl import OntologyDocument, Ontology

        EX = Namespace("http://www.example.com/ontology1#")
        o = Ontology("http://www.example.com/ontology1")
        o.imports("http://www.example.com/ontology2")
        o.annotation(RDFS.label, "An example")
        o.subClassOf(EX.Child, OWL.Thing)
        doc = OntologyDocument(EX, o)
        print(str(doc.to_functional()))

    def test_readme_example2(self):
        from rdflib import Namespace, XSD, Literal
        from funowl import Ontology, DataProperty, Class, DataAllValuesFrom, DataOneOf, SubClassOf, DataSomeValuesFrom, \
            ClassAssertion, OntologyDocument

        EX = Namespace("http://example.org/")

        # Ontology represents the OWLF OntologyDocument production
        o = Ontology(EX.myOntology, "http://example.org/myOntolology/version/0.1")

        # namedIndividual, objectProperty, class, et. properties add to declarations
        o.namedIndividuals(EX.a)

        # Declarations can also be added explicitly
        o.declarations(DataProperty(EX.dp), Class(EX.A))

        # Axioms are added by type
        o.subClassOf(EX.A, DataAllValuesFrom(EX.dp, DataOneOf(3, Literal(4, datatype=XSD.int))))

        # or as an array
        o.axioms.append(SubClassOf(EX.A, DataAllValuesFrom(EX.dp, DataOneOf(Literal(2, datatype=XSD.short),
                                                                            Literal(3, datatype=XSD.int)))))
        o.axioms.append(ClassAssertion(DataSomeValuesFrom(EX.dp, DataOneOf(3)), EX.a))

        print(str(OntologyDocument(EX, ontology=o).to_functional()))


if __name__ == '__main__':
    unittest.main()
