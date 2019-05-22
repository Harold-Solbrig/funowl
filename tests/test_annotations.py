import unittest

from rdflib import RDFS

from funowl.Annotations import Annotation


class AnnotationsTestCase(unittest.TestCase):
    def test_basic_annotation(self):
        self.assertEqual('Annotation( <http://www.w3.org/2000/01/rdf-schema#label> "This is a test" )',
                         Annotation(RDFS.label, "This is a test").as_owl())


if __name__ == '__main__':
    unittest.main()
