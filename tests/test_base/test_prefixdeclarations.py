import unittest

from rdflib import RDF, URIRef, RDFS

from funowl.prefix_declarations import Prefix, PrefixDeclarations
from tests.utils.base import TestBase


class PrefixTestCase(TestBase):
    def test_prefix(self):
        self.assertEqual('Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )',
                         str(Prefix('rdf', RDF).to_functional(self.w)))
        self.assertEqual('Prefix( ex: = <http://www.example.org/test/> )',
                         str(Prefix('ex', "http://www.example.org/test/").to_functional(self.w.reset())))
        self.assertEqual('Prefix( : = <http://example.org/mt/> )',
                         str(Prefix(None, URIRef("http://example.org/mt/")).to_functional(self.w.reset())))
        with self.assertRaises(TypeError):
            Prefix('http:', RDFS)

    def test_default_prefix(self):
        """ Test that None is the correct default prefix """
        x = Prefix(None, RDFS.Resource)
        self.assertEqual('Prefix( : = <http://www.w3.org/2000/01/rdf-schema#Resource> )', str(x.to_functional(self.w)))
        self.assertEqual('Prefix( : = <http://www.w3.org/2000/01/rdf-schema#Resource> )',
                         str(x.to_functional(self.w.reset())))
        pds = PrefixDeclarations()
        pds.append(x)
        pds.bind(None, RDFS.label)
        self.assertEqual('''Prefix( xml: = <http://www.w3.org/XML/1998/namespace> )
Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
Prefix( owl: = <http://www.w3.org/2002/07/owl#> )
Prefix( : = <http://www.w3.org/2000/01/rdf-schema#label> )''', str(pds.to_functional(self.w.reset())))


    def test_prefixDeclarations(self):
        pds = PrefixDeclarations()
        self.assertEqual("""Prefix( xml: = <http://www.w3.org/XML/1998/namespace> )
Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
Prefix( owl: = <http://www.w3.org/2002/07/owl#> )""", str(pds.to_functional(self.w)))
        pds.bind('xml', "http://example.org/xml2#")
        pds.bind(None, "http://www.w3.org/2002/07/owl#")
        self.assertEqual("""    Prefix( xml: = <http://example.org/xml2#> )
    Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
    Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
    Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
    Prefix( owl: = <http://www.w3.org/2002/07/owl#> )
    Prefix( : = <http://www.w3.org/2002/07/owl#> )""", str(pds.to_functional(self.w.reset().indent())))

        pds.foaf = "http://foaf.org/"
        self.assertEqual('''Prefix( xml: = <http://example.org/xml2#> )
Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
Prefix( owl: = <http://www.w3.org/2002/07/owl#> )
Prefix( : = <http://www.w3.org/2002/07/owl#> )
Prefix( foaf: = <http://foaf.org/> )''', str(pds.to_functional(self.w.reset())))


if __name__ == '__main__':
    unittest.main()
