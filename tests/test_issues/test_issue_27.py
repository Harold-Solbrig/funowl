import os
import unittest
from contextlib import redirect_stderr
from io import StringIO

from funowl.converters.functional_converter import to_python
import requests

from tests import datadir

# Set this to False if you want to make sure some of the big inputs work
SKIP_LONG_TESTS = True

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

OWL_MT = """Prefix(:=<http://www.biopax.org/release/biopax-level3.owl#>)
Prefix(rdfs:=<http://www.w3.org/2000/01/rdf-schema#>)
Ontology(
AnnotationAssertion(rdfs:label :foo "")
AnnotationAssertion(rdfs:label :foo "x")
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

    @unittest.skipIf(SKIP_LONG_TESTS, "Use this if there are issues w/ linkml content.  Too slow for general testing")
    def test_sdo_issue(self):
        with requests.get("https://raw.githubusercontent.com/linkml/linkml-model-enrichment/infer-from-owl/tests/resources/schemaorg-robot.ofn") as inp:
            owl = to_python(inp.text)
        print(str(owl))

    @unittest.skipIf(SKIP_LONG_TESTS, "uberon image must be present to run this")
    def test_uberon_issue(self):
        # To run this test:
        #   a) Download an image of https://bioportal.bioontology.org/ontologies/UBERON from the owl link
        #   b) Use protege to load the downloaded image (ext.owl) and save it in OWL functional syntax (ext.owlf.owl)
        #   c) Save the output in tests/data/ext.owlf

        # TO Complete -- redirect the part of the stdout that kicks out the errors on URI's
        #  Verify that we don't have an error message in it
        #  Look up a bit of the OWL that has a PMID in it and make sure that it prints correctly
        txt = StringIO()
        with redirect_stderr(txt):
            with open(os.path.join(datadir, 'ext.owlf')) as f:
                owl = to_python(f.read())
        print(str(owl)[-1024:])

    def test_empty_literal(self):
        owl = to_python(OWL_MT)
        self.assertIn('AnnotationAssertion( rdfs:label :foo "" )', str(owl))


if __name__ == '__main__':
    unittest.main()
