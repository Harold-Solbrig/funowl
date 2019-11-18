import unittest

from rdflib import Graph, URIRef, Namespace

from funowl import Prefix
from funowl.ontology_document import Ontology, Import, OntologyDocument
from tests.utils.base import TestBase, A


class ImportTestCase(TestBase):

    def test_import_to_rdf(self):
        g = Graph()
        imp = Import('http://www.example.com/ontology')
        self.assertIsInstance(imp.to_rdf(g), URIRef)
        self.assertEqual('http://www.example.com/ontology', str(imp.to_rdf(g)))


EX = Namespace("http://www.example.com/ontology1#")

class OntologyDocumentTestCase(TestBase):

    def test_ontology_document_prefixes(self):
        doc = OntologyDocument(A, ex=EX)
        self.assertEqual("""Prefix( xml: = <http://www.w3.org/XML/1998/namespace> )
Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
Prefix( owl: = <http://www.w3.org/2002/07/owl#> )
Prefix( : = <http://example.org/a#> )
Prefix( ex: = <http://www.example.com/ontology1#> )

Ontology( )""", doc.to_functional().getvalue())

    def test_use_case_one(self):
        from rdflib import RDFS, OWL
        od = OntologyDocument(ontology=Ontology(iri="http://www.example.com/ontology1"))
        od.prefixes(EX)
        od.ontology.imports("http://www.example.com/ontology2")
        od.ontology.annotation(RDFS.label, "An example")
        od.ontology.subClassOf(EX.Child, OWL.Thing)
        self.assertEqual("""Prefix( xml: = <http://www.w3.org/XML/1998/namespace> )
Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
Prefix( owl: = <http://www.w3.org/2002/07/owl#> )
Prefix( : = <http://www.example.com/ontology1#> )

Ontology( <http://www.example.com/ontology1>
    Import( <http://www.example.com/ontology2> )
    Annotation( rdfs:label "An example" )
    SubClassOf( :Child owl:Thing )
)""", str(od.to_functional(self.w)))


if __name__ == '__main__':
    unittest.main()
