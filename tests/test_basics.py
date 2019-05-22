import unittest

from rdflib import OWL, RDF, RDFS
from rdflib.namespace import SKOS

from funowl.Annotations import Annotation
from funowl.OntologyDocument import Ontology, Ontology, PrefixDeclaration


class OwlBasicsTestCase(unittest.TestCase):
    def test_ontology_document(self):
        doc = Ontology()
        self.assertEqual('Ontology( \n )', doc.as_owl().strip())
        doc.iri = "http://snomed.info/sct/"
        self.assertEqual("Ontology( <http://snomed.info/sct/>\n )", doc.as_owl().strip())
        doc.version = "http://snomed.info/sct/version/201802017"
        self.assertEqual("Ontology( <http://snomed.info/sct/> <http://snomed.info/sct/version/201802017>\n )",
                         doc.as_owl().strip())
        doc.prefixes(RDFS, owl=OWL, rdf=RDF)
        self.assertEqual('''Prefix(:=<http://www.w3.org/2000/01/rdf-schema#>)
Prefix(owl:=<http://www.w3.org/2002/07/owl#>)
Prefix(rdf:=<http://www.w3.org/1999/02/22-rdf-syntax-ns#>)

Ontology( <http://snomed.info/sct/> <http://snomed.info/sct/version/201802017>\n )''', doc.as_owl())
        doc.imports(SKOS)
        doc.imports("http://example.org/dep")
        doc.annotations.append(Annotation(RDFS.label, "foo"))
        print(doc.as_owl())


if __name__ == '__main__':
    unittest.main()
