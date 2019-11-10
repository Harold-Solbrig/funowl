import unittest
from typing import List

from rdflib import OWL, RDF, RDFS
from rdflib.namespace import SKOS

from funowl.annotations import Annotation
from funowl.ontology_document import Ontology, OntologyDocument
from tests.utils.base import TestBase


def expected(defs: List[str]) -> str:
    inside = (' ' + '\n'.join(defs)) if defs else ''
    return f"""Prefix( xml: = <http://www.w3.org/XML/1998/namespace> )
Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
Prefix( owl: = <http://www.w3.org/2002/07/owl#> )

Ontology({inside} )"""


class OwlBasicsTestCase(TestBase):
    def test_ontology_document(self):
        doc = OntologyDocument()
        self.assertEqual(expected([]), str(doc.to_functional().getvalue()))
        doc.ontology.iri = "http://snomed.info/sct/"
        self.assertEqual(expected(['<http://snomed.info/sct/>']), str(doc.to_functional().getvalue()))
        doc.ontology.version = "http://snomed.info/sct/version/201802017"
        self.assertEqual(expected(['<http://snomed.info/sct/> <http://snomed.info/sct/version/201802017>']),
                         doc.to_functional().getvalue())
        doc.prefixes(RDFS, owl=OWL, rdf=RDF)

        self.assertEqual('''Prefix( xml: = <http://www.w3.org/XML/1998/namespace> )
Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
Prefix( owl: = <http://www.w3.org/2002/07/owl#> )
Prefix( : = <http://www.w3.org/2000/01/rdf-schema#> )

Ontology( <http://snomed.info/sct/> <http://snomed.info/sct/version/201802017> )''', str(doc.to_functional()))
        doc.ontology.imports(SKOS)
        doc.ontology.imports("http://example.org/dep")
        doc.ontology.annotations.append(Annotation(RDFS.label, "foo"))
        self.assertEqual('''Prefix( xml: = <http://www.w3.org/XML/1998/namespace> )
Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
Prefix( owl: = <http://www.w3.org/2002/07/owl#> )
Prefix( : = <http://www.w3.org/2000/01/rdf-schema#> )

Ontology( <http://snomed.info/sct/> <http://snomed.info/sct/version/201802017>
    Import( <http://www.w3.org/2004/02/skos/core#> )
    Import( <http://example.org/dep> )
    Annotation( :label "foo" )
)''', str(doc.to_functional()))


if __name__ == '__main__':
    unittest.main()
