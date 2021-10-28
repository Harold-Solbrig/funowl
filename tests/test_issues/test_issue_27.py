import unittest
from funowl.converters.functional_converter import to_python
import requests

OWL_1 = """
Prefix(:=<http://www.biopax.org/release/biopax-level3.owl#>)
Prefix(rdfs:=<http://www.w3.org/2000/01/rdf-schema#>)

Ontology(
    AnnotationAssertion(rdfs:label :foo ")")
)
"""

OWL_2 = """Prefix(:=<http://www.biopax.org/release/biopax-level3.owl#>)
Prefix(rdfs:=<http://www.w3.org/2000/01/rdf-schema#>)
Ontology(AnnotationAssertion(rdfs:label :foo "a b c d) e"))
"""

OWL_3 = """Prefix(:=<http://www.biopax.org/release/biopax-level3.owl#>)
Prefix(rdfs:=<http://www.w3.org/2000/01/rdf-schema#>)
Ontology(AnnotationAssertion(rdfs:label :foo 
    "a()\\"\\\\\\""
    ))"""

OWL_ERR = """Prefix(:=<http://www.biopax.org/release/biopax-level3.owl#>)
Prefix(rdfs:=<http://www.w3.org/2000/01/rdf-schema#>)
Ontology(
AnnotationAssertion(rdfs:label :foo ("a b c d) e")
)"""


class ParenAsLiteralTestCase(unittest.TestCase):
    def test_1(self):
        owl = to_python(OWL_1)
        self.assertTrue("Didn't fail this input")

    def test_2(self):
        owl = to_python(OWL_2)
        self.assertTrue("Didn't fail this input")

    def test_3(self):
        owl = to_python(OWL_3)
        self.assertTrue("Didn't fail this input")

    def test_4(self):
        with self.assertRaises(ValueError) as e:
            owl = to_python(OWL_ERR)
        self.assertIn('Not expecting a quoted string', str(e.exception))

    @unittest.skip("Use this if there are issues w/ linkml content.  Too slow for general testing")
    def test_sdo_issue(self):
        with requests.get("https://raw.githubusercontent.com/linkml/linkml-model-enrichment/infer-from-owl/tests/resources/schemaorg-robot.ofn") as inp:
            owl = to_python(inp.text)
        print(str(owl))


if __name__ == '__main__':
    unittest.main()
