import unittest

from rdflib import RDFS

from funowl.GeneralDefinitions import NonNegativeInteger, QuotedString, LanguageTag, NodeID, FullIRI, PrefixName
from funowl.OntologyDocument import Ontology


class TestGeneralDefinitons(unittest.TestCase):
    def test_nonnegativeinteger(self):
        self.assertEqual(143, NonNegativeInteger(143))
        self.assertEqual(143, NonNegativeInteger('143'))
        self.assertEqual(0, NonNegativeInteger(0))
        with self.assertRaises(TypeError):
            NonNegativeInteger(-1)
        with self.assertRaises(ValueError):
            NonNegativeInteger('a')
        with self.assertRaises(TypeError):
            NonNegativeInteger(None)
        with self.assertRaises(TypeError):
            NonNegativeInteger(Ontology())
        self.assertEqual('42', NonNegativeInteger(42).as_owl())
        self.assertEqual('\t0', NonNegativeInteger(0).as_owl(1))

        self.assertTrue(isinstance(143, NonNegativeInteger))
        self.assertTrue(isinstance('117', NonNegativeInteger))
        self.assertFalse(isinstance("-1", NonNegativeInteger))
        self.assertFalse(isinstance(None, NonNegativeInteger))
        self.assertFalse(isinstance('abc', NonNegativeInteger))
        self.assertFalse(isinstance(Ontology(), NonNegativeInteger))

    def test_quotedstring(self):
        self.assertEqual('abc def', QuotedString('abc def'))
        self.assertEqual('abc"\\def', QuotedString('abc"\\def'))
        self.assertEqual('"abc\\"\\\\def"', QuotedString('abc"\\def').as_owl())
        with self.assertRaises(TypeError):
            QuotedString(None)

    def test_languagetag(self):
        self.assertTrue(isinstance('en', LanguageTag))  # isinstance works even if the element is a string
        self.assertFalse(type('en') is LanguageTag)
        self.assertTrue(type(LanguageTag('en')) is LanguageTag)
        self.assertFalse(isinstance('1n', LanguageTag))
        self.assertFalse(isinstance('en-', LanguageTag))
        self.assertEqual('@en-us', LanguageTag('en-us').as_owl())
        with self.assertRaises(ValueError):
            LanguageTag('1')

    def test_nodeid(self):
        self.assertTrue(NodeID().startswith('_:'))
        self.assertEqual('_:ABC', NodeID('_:ABC').as_owl())
        self.assertTrue(isinstance('_:117A', NodeID))
        self.assertFalse(isinstance(':_abc', NodeID))
        with self.assertRaises(TypeError):
            NodeID(':_abc')

    def test_fullIRI(self):
        self.assertEqual('http://example.org/foo#', FullIRI("http://example.org/foo#"))
        self.assertEqual('\t\t<http://example.org/foo#>', FullIRI("http://example.org/foo#").as_owl(2))
        with self.assertRaises(TypeError):
            FullIRI("//just/a/path:")

    def test_prefixname(self):
        self.assertEqual('rdfs', PrefixName('rdfs'))
        self.assertEqual('rdfs:', PrefixName('rdfs').as_owl())
        self.assertEqual(':', PrefixName().as_owl())
        with self.assertRaises(TypeError):
            PrefixName('1bc')
        self.assertEqual('abc_:', PrefixName('abc_').as_owl())


if __name__ == '__main__':
    unittest.main()
