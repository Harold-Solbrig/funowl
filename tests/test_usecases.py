import unittest

from funowl.OntologyDocument import Ontology


class MyTestCase(unittest.TestCase):
    def test_usecase_one(self):
        from rdflib import RDFS, OWL, Namespace

        EX = Namespace("http://www.example.com/ontology1#")

        o = Ontology(iri="http://www.example.com/ontology1")
        o.prefixes(EX)
        o.imports("http://www.example.com/ontology2")
        o.annotation(RDFS.label, "An example")
        o.subClassOf(EX.Child, OWL.Thing)
        self.assertEqual("""Prefix(:=<http://www.example.com/ontology1#>)

Ontology( <http://www.example.com/ontology1>
\tImport( <http://www.example.com/ontology2> )
\tAnnotation( rdfs:label "An example" )

\tSubClassOf( :Child owl:Thing )
) """, o.as_owl())



if __name__ == '__main__':
    unittest.main()
