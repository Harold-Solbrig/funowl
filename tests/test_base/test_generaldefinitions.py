import unittest

from rdflib import URIRef

from funowl.general_definitions import NonNegativeInteger, QuotedString, LanguageTag, NodeID, FullIRI, PrefixName
from funowl.ontology_document import Ontology
from tests.utils.base import TestBase


class TestGeneralDefinitons(TestBase):
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
        self.assertEqual('42', str(NonNegativeInteger(42).to_functional(self.w)))
        self.assertEqual('    0', str(NonNegativeInteger(0).to_functional(self.w.reset().indent())))

        self.assertTrue(isinstance(143, NonNegativeInteger))
        self.assertTrue(isinstance('117', NonNegativeInteger))
        self.assertFalse(isinstance("-1", NonNegativeInteger))
        self.assertFalse(isinstance(None, NonNegativeInteger))
        self.assertFalse(isinstance('abc', NonNegativeInteger))
        self.assertFalse(isinstance(Ontology(), NonNegativeInteger))

    def test_quotedstring(self):
        self.assertEqual('abc def', QuotedString('abc def'))
        self.assertEqual('abc"\\def', QuotedString('abc"\\def'))
        self.assertEqual('"abc\\"\\\\def"', str(QuotedString('abc"\\def').to_functional(self.w)))
        with self.assertRaises(ValueError):
            QuotedString(None)

    def test_languagetag(self):
        self.assertTrue(isinstance('en', LanguageTag))  # isinstance works even if the element is a string
        self.assertFalse(type('en') is LanguageTag)
        self.assertTrue(type(LanguageTag('en')) is LanguageTag)
        self.assertFalse(isinstance('1n', LanguageTag))
        self.assertFalse(isinstance('en-', LanguageTag))
        self.assertEqual('@en-US', str(LanguageTag('en-US').to_functional(self.w)))
        with self.assertRaises(TypeError):
            LanguageTag('1')

    def test_nodeid(self):
        self.assertTrue(NodeID().startswith('_:'))
        self.assertEqual('_:ABC', str(NodeID('_:ABC').to_functional(self.w)))
        self.assertTrue(isinstance('_:117A', NodeID))
        self.assertFalse(isinstance(':_abc', NodeID))
        with self.assertRaises(TypeError):
            NodeID(':_abc')

    def test_fullIRI(self):
        self.assertEqual('http://example.org/foo#', FullIRI("http://example.org/foo#"))
        self.assertEqual('    <http://example.org/foo#>',
                         str(FullIRI("http://example.org/foo#").to_functional(self.w.indent())))
        with self.assertRaises(TypeError):
            FullIRI("//just/a/path:")

    def test_fullIRI_URIRef(self):
        self.assertEqual('http://example.org/foo#', FullIRI(URIRef("http://example.org/foo#")))
        self.assertTrue(isinstance(URIRef("http://example.org/foo#"), FullIRI))

    def test_prefixname(self):
        self.assertEqual('rdfs', PrefixName('rdfs'))
        self.assertEqual('rdfs', str(PrefixName('rdfs').to_functional(self.w)))
        with self.assertRaises(ValueError):
            PrefixName(None)
        with self.assertRaises(TypeError):
            PrefixName('1bc')
        self.assertEqual('abc_', str(PrefixName('abc_').to_functional(self.w.reset())))


if __name__ == '__main__':
    unittest.main()
