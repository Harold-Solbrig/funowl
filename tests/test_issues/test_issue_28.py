import unittest
from io import StringIO

from funowl.converters.functional_converter import to_python

OWL_1 = """
Prefix(:=<http://www.biopax.org/release/biopax-level3.owl#>)
Prefix(rdfs:=<http://www.w3.org/2000/01/rdf-schema#>)

Ontology(
    AnnotationAssertion(rdfs:label :foo "PMID:12345")
    AnnotationAssertion(rdfs:label :foo "http://www.w3.org/2000/01/rdf-schema#")
    AnnotationAssertion(rdfs:label :foo 117)
    
)
"""


class LiteralURIProblem(unittest.TestCase):
    txt = StringIO()

    def test_1(self):
        owl = to_python(OWL_1)
        # We would LIKE to test for the absence of the following message in stderr:
        #   WARNING:root:IRI: PMID:12345 - PMID not a valid prefix
        # but this requires a bit of cleverness that we've used elsewhere and will skip for now.  The key is that
        # the quotes should be in the line below --
        self.assertIn('AnnotationAssertion( rdfs:label :foo "PMID:12345" )', str(owl),
                      "Literal was interpreted as a URI")


if __name__ == '__main__':
    unittest.main()
