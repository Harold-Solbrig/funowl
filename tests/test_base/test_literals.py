import unittest
from datetime import date, datetime, time

import rdflib
from rdflib import XSD

from funowl.literals import Literal, TypedLiteral, StringLiteralNoLanguage, StringLiteralWithLanguage
from tests.utils.base import TestBase, A

various_literals = [
    (5, '"5"^^xsd:integer'),
    (False, '"False"^^xsd:boolean'),
    (17.2, '"17.2"^^xsd:double'),
    (date(2002, 3, 11), '"2002-03-11"^^xsd:date'),
    (datetime(1911, 7, 12, 11, 13, 43, 973), '"1911-07-12 11:13:43.000973"^^xsd:dateTime'),
    (time(17, 43, 19, 223), '"17:43:19.000223"^^xsd:time')
]


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

    def test_literal_type(self):
        """ Subclasses of Literal are instances of literal """
        x = TypedLiteral(5, XSD.integer)
        self.assertEqual('5^^http://www.w3.org/2001/XMLSchema#integer', str(x))
        self.assertTrue(isinstance(TypedLiteral(5, XSD.integer), Literal))

    def test_bare_literal(self):
        for v, expected in various_literals:
            lv = Literal(v)
            self.w.reset()
            self.assertEqual(str(lv.to_functional(self.w)), expected)

    def test_typed_literal(self):
        for v, expected in various_literals:
            lv = TypedLiteral(v)
            self.w.reset()
            self.assertEqual(expected, str(lv.to_functional(self.w)))
        # TODO: RDFLIB has some pretty strong literal typing -- if we try to use it out of the box, it tends to
        #       disappear things.
        rdflib.term.bind(A.bird, str)
        x = rdflib.Literal('Penguin', datatype=A.bird)
        self.assertEqual('"Penguin"^^<http://example.org/a#bird>', str(TypedLiteral(x).to_functional(self.w.reset())))

if __name__ == '__main__':
    unittest.main()
