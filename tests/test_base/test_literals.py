import unittest

from rdflib import XSD

from funowl.literals import Literal, TypedLiteral, StringLiteralNoLanguage, StringLiteralWithLanguage
from tests.utils.base import TestBase


class LiteralsTestCase(TestBase):

    def test_stringliteralnolanguage(self):
        self.assertEqual('"testing"', StringLiteralNoLanguage("testing").to_functional(self.w).getvalue())
        self.w.reset()
        self.assertEqual('"AB\\"\\\\C\\""', StringLiteralNoLanguage('AB"\\C"').to_functional(self.w).getvalue())
        self.w.reset()
        self.assertEqual('"117"', StringLiteralNoLanguage(117).to_functional(self.w).getvalue())

    def test_typedliteral(self):
        self.assertEqual(r'"\"AB\\\"\\\\C\\\"\""^^xsd:integer',
                         TypedLiteral('"AB\\"\\\\C\\""', XSD.integer).to_functional(self.w).getvalue())
        self.w.reset()
        self.assertEqual(r'"\"AB\\\"\\\\C\\\"\""^^<http://example.org/types/indigo>',
                         TypedLiteral('"AB\\"\\\\C\\""',
                                      "http://example.org/types/indigo").to_functional(self.w).getvalue())

    def test_stringliteralwithlanguage(self):
        self.assertEqual(r'"\"AB\\\\\"\\\\C\\\"\""@en-GB',
                         StringLiteralWithLanguage(r'"AB\\"\\C\""', 'en-GB').to_functional(self.w).getvalue())

    def test_literal(self):
        self.assertEqual('"testing"', Literal("testing").to_functional(self.w).getvalue())
        self.w.reset()
        self.assertEqual('"testing"', Literal("'testing'^^xsd:string").to_functional(self.w).getvalue())
        self.w.reset()
        self.assertEqual('"AB\\"\\\\C\\""', Literal('AB\\"\\\\C\\"').to_functional(self.w).getvalue())
        self.w.reset()
        self.assertEqual('"42"^^xsd:integer',
                         Literal('"42"^^xsd:integer').to_functional(self.w).getvalue())
        with self.assertRaises(ValueError):
            Literal('"AB\\"\\\\C\\""^^xsd:integer')
        with self.assertRaises(ValueError):
            Literal('"ABC"^xsd:integer')
        with self.assertRaises(ValueError):
            Literal('"123"^^xsd.integer')
        self.assertTrue(isinstance('"42"^^xsd:integer', Literal))
        self.assertFalse(isinstance('"123"^^xsd.integer', Literal))
        self.w.reset()
        self.assertEqual('"abc"@en-GB', Literal('"abc"@en-GB').to_functional(self.w).getvalue())
        with self.assertRaises(TypeError):
            Literal('"abc"@en-gb')

    def test_literal_type(self):
        """ Subclasses of Literal are instances of literal """
        x = TypedLiteral(5, XSD.integer)
        self.assertEqual('5^^http://www.w3.org/2001/XMLSchema#integer', str(x))
        self.assertTrue(isinstance(TypedLiteral(5, XSD.integer), Literal))


if __name__ == '__main__':
    unittest.main()
