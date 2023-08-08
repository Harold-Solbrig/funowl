import unittest

from rdflib import RDF, URIRef, RDFS

from funowl.prefix_declarations import Prefix, PrefixDeclarations
from tests import RDFLIB_PREFIXES_ARE_BROKEN, PREFIXES_BROKEN_MESSAGE
from tests.utils.base import TestBase


class PrefixTestCase(TestBase):
    def test_prefix(self):
        self.assertEqualOntology('Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )',
                         str(Prefix('rdf', RDF).to_functional(self.w)))
        self.assertEqualOntology('Prefix( ex: = <http://www.example.org/test/> )',
                         str(Prefix('ex', "http://www.example.org/test/").to_functional(self.w.reset())))
        self.assertEqualOntology('Prefix( : = <http://example.org/mt/> )',
                         str(Prefix(None, URIRef("http://example.org/mt/")).to_functional(self.w.reset())))
        with self.assertRaises(TypeError):
            Prefix('http:', RDFS)

    def test_prefix_append(self):
        """
        Test that prefixes can be appended correctly.

        Note that rdflib introduces namespace pollution by default,
        this checks we instantiate rdf graphs in a way that avoids this.
        """
        pds = PrefixDeclarations()
        pds.append(Prefix("schema", "http://schema.org/"))
        self.assertEqualOntology('''Prefix( xml: = <http://www.w3.org/XML/1998/namespace> )
        Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
        Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
        Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
        Prefix( owl: = <http://www.w3.org/2002/07/owl#> )
        Prefix( schema: = <http://schema.org/> )''', str(pds.to_functional(self.w.reset())))
        pds = PrefixDeclarations()
        pds.append(Prefix("schema", "https://schema.org/"))
        self.assertEqualOntology('''Prefix( xml: = <http://www.w3.org/XML/1998/namespace> )
        Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
        Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
        Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
        Prefix( owl: = <http://www.w3.org/2002/07/owl#> )
        Prefix( schema: = <https://schema.org/> )''', str(pds.to_functional(self.w.reset())))
        pds = PrefixDeclarations()
        pds.append(Prefix("sdo", "http://schema.org/"))
        self.assertEqualOntology('''Prefix( xml: = <http://www.w3.org/XML/1998/namespace> )
        Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
        Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
        Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
        Prefix( owl: = <http://www.w3.org/2002/07/owl#> )
        Prefix( sdo: = <http://schema.org/> )''', str(pds.to_functional(self.w.reset())))



    @unittest.skipIf(RDFLIB_PREFIXES_ARE_BROKEN, PREFIXES_BROKEN_MESSAGE)
    def test_default_prefix(self):
        """ Test that None is the correct default prefix """
        x = Prefix(None, RDFS.Resource)
        self.assertEqual('Prefix( : = <http://www.w3.org/2000/01/rdf-schema#Resource> )', str(x.to_functional(self.w)))
        self.assertEqual('Prefix( : = <http://www.w3.org/2000/01/rdf-schema#Resource> )',
                         str(x.to_functional(self.w.reset())))
        pds = PrefixDeclarations()
        pds.append(x)
        pds.bind(None, RDFS.label)
        self.assertEqualOntology('''Prefix( xml: = <http://www.w3.org/XML/1998/namespace> )
Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
Prefix( owl: = <http://www.w3.org/2002/07/owl#> )
Prefix( : = <http://www.w3.org/2000/01/rdf-schema#label> )''', str(pds.to_functional(self.w.reset())))


    @unittest.skipIf(RDFLIB_PREFIXES_ARE_BROKEN, PREFIXES_BROKEN_MESSAGE)
    def test_prefixDeclarations(self):
        pds = PrefixDeclarations()
        self.assertEqualOntology("""Prefix( xml: = <http://www.w3.org/XML/1998/namespace> )
Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
Prefix( owl: = <http://www.w3.org/2002/07/owl#> )""", str(pds.to_functional(self.w)))
        pds.bind('xml', "http://example.org/xml2#")
        pds.bind(None, "http://www.w3.org/2002/07/owl#")
        self.assertEqualOntology("""    Prefix( xml: = <http://example.org/xml2#> )
    Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
    Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
    Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
    Prefix( owl: = <http://www.w3.org/2002/07/owl#> )
    Prefix( : = <http://www.w3.org/2002/07/owl#> )""", str(pds.to_functional(self.w.reset().indent())))

        pds.foaf = "http://foaf.org/"
        self.assertEqualOntology('''Prefix( xml: = <http://example.org/xml2#> )
Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
Prefix( owl: = <http://www.w3.org/2002/07/owl#> )
Prefix( : = <http://www.w3.org/2002/07/owl#> )
Prefix( foaf: = <http://foaf.org/> )''', str(pds.to_functional(self.w.reset())))


if __name__ == '__main__':
    unittest.main()
