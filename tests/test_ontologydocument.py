import unittest

from funowl.ontology_document import Ontology
from tests.utils.base import TestBase


class UseCaseTestCase(TestBase):
    def test_use_case_one(self):
        from rdflib import RDFS, OWL, Namespace

        EX = Namespace("http://www.example.com/ontology1#")

        o = Ontology(iri="http://www.example.com/ontology1")
        o.prefixes(EX)
        o.imports("http://www.example.com/ontology2")
        o.annotation(RDFS.label, "An example")
        o.subClassOf(EX.Child, OWL.Thing)
        self.assertEqual("""Prefix( xml := <http://www.w3.org/XML/1998/namespace> )
Prefix( rdf := <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
Prefix( rdfs := <http://www.w3.org/2000/01/rdf-schema#> )
Prefix( xsd := <http://www.w3.org/2001/XMLSchema#> )
Prefix( owl := <http://www.w3.org/2002/07/owl#> )
Prefix(  := <http://www.example.com/ontology1#> )

Ontology( <http://www.example.com/ontology1>
        Import( <http://www.example.com/ontology2> )
        SubClassOf( <http://www.example.com/ontology1#Child>   owl:Thing )
)""", str(o.to_functional(self.w)))



if __name__ == '__main__':
    unittest.main()
