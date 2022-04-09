import unittest

from funowl import AnnotationValue
from funowl.converters.functional_converter import to_python


class Issue39TestCase(unittest.TestCase):
    def test_assignment_in_code(self):
        r = to_python("""Prefix(:=<http://purl.obolibrary.org/obo/so#>)
Ontology(<http://purl.obolibrary.org/obo/so/subsets/SOFA.owl>

AnnotationAssertion(:hasDbXref :SO_0000394 "PMID:=12409455")
)""")
        self.assertIs(type(r.ontology.axioms[0].value), AnnotationValue)
        self.assertEqual("PMID:=12409455", str(r.ontology.axioms[0].value))

if __name__ == '__main__':
    unittest.main()
