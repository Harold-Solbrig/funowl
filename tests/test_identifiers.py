import unittest

from rdflib import RDFS, OWL

from funowl.identifiers import IRI
from tests.utils.base import TestBase


class IdentifiersTestCase(TestBase):
    def test_iri(self):
        w = self.w
        x1 = IRI("http://example.org/ex#")
        self.assertEqual('<http://example.org/ex#>', x1.to_functional(w).getvalue())
        x2 = IRI(RDFS.label)
        self.assertEqual('rdfs:label', x2.to_functional(w.reset()).getvalue())
        x3 = IRI('rdf:type')
        self.assertEqual('rdf:type', x3.to_functional(w.reset()).getvalue())
        w.g.bind('xcf', RDFS)
        x4 = IRI('xcf:type')
        self.assertEqual('xcf:type', x4.to_functional(w.reset()).getvalue())
        x5 = IRI('foo:type')
        self.assertEqual('foo:type', x5.to_functional(w.reset()).getvalue())


if __name__ == '__main__':
    unittest.main()
