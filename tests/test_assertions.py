import unittest

from rdflib import Namespace, RDFS, XSD

from funowl.Annotations import Annotation
from funowl.Assertions import SameIndividual, DifferentIndividuals, ClassAssertion, ObjectPropertyAssertion, \
    NegativeObjectPropertyAssertion, DataPropertyAssertion, NegativeDataPropertyAssertion
from funowl.writers.FunctionalWriter import FunctionalWriter
from funowl.Literals import Literal, TypedLiteral
from tests.utils.base import TestBase

A = Namespace("http://example.org/a/")


class AssertionsTestCase(TestBase):
    @classmethod
    def setUpClass(cls) -> None:
        TestBase.setUpClass()
        cls.w.g.bind('a', A)

    def test_sameindividual(self):
        self.assertEqual('SameIndividual( a:Peter a:Peter_Griffin )',
                         SameIndividual(A.Peter, A.Peter_Griffin).to_functional(self.w).getvalue())
        with self.assertRaises(ValueError):
            # Only one individual
            SameIndividual(A.Peter).to_functional(self.w)
        self.w.reset()
        self.assertEqual("""SameIndividual(
    Annotation( rdfs:comment "Many aliases" )
    a:Alex a:Bob a:Charlie
)""", SameIndividual(A.Alex, A.Bob, A.Charlie,
                     annotations=Annotation(RDFS.comment, "Many aliases")).to_functional(self.w).getvalue())

    def test_differentindividuals(self):
        self.assertEqual('DifferentIndividuals( a:Peter a:Peter_Griffin )',
                         DifferentIndividuals(A.Peter, A.Peter_Griffin).to_functional(self.w).getvalue())
        with self.assertRaises(ValueError):
            # Only one individual
            DifferentIndividuals(A.Peter).to_functional(self.w)
        self.w.reset()
        self.assertEqual("""DifferentIndividuals(
    Annotation( rdfs:comment "We know better" )
    a:Alex a:Bob a:Charlie
)""", DifferentIndividuals(A.Alex, A.Bob, A.Charlie,
                     annotations=Annotation(RDFS.comment, "We know better")).to_functional(self.w).getvalue())

    def test_classassertion(self):
        self.assertEqual('ClassAssertion( a:GriffinFamilyMember a:Peter_Griffin )',
                         ClassAssertion( A.GriffinFamilyMember, A.Peter_Griffin).to_functional(self.w).getvalue())
        self.w.reset()
        self.assertEqual("""ClassAssertion(
    Annotation( rdfs:comment "It runs in..." )
    a:GriffinFamilyMember a:Peter_Griffin
)""", ClassAssertion( A.GriffinFamilyMember, A.Peter_Griffin,
                      Annotation(RDFS.comment, "It runs in...")).to_functional(self.w).getvalue())

    def test_objectpropertyassertion(self):
        self.assertEqual('ObjectPropertyAssertion( a:hasBrother a:Meg a:Stewie )',
                         ObjectPropertyAssertion(A.hasBrother, A.Meg, A.Stewie).to_functional(self.w).getvalue())

    def test_negativeobjectpropertyassertion(self):
        self.assertEqual('NegativeObjectPropertyAssertion( a:hasBrother a:Meg a:Stewie )',
                         NegativeObjectPropertyAssertion(A.hasBrother, A.Meg, A.Stewie).
                         to_functional(self.w).getvalue())

    def test_datapropertyassertion(self):
        x = Literal('"17"^^xsd:integer')
        y = DataPropertyAssertion(A.hasAge, A.Meg, x)
        self.assertEqual('DataPropertyAssertion( a:hasAge a:Meg "17"^^xsd:integer )',
                         DataPropertyAssertion(A.hasAge, A.Meg, Literal('"17"^^xsd:integer')).
                         to_functional(self.w).getvalue())

    def test_negativedatapropertyassertion(self):
        TypedLiteral(5, XSD.integer)
        self.assertEqual('NegativeDataPropertyAssertion( a:hasBrother a:Meg "5"^^xsd:integer )',
                         NegativeDataPropertyAssertion(A.hasBrother, A.Meg, TypedLiteral(5, XSD.integer)).
                         to_functional(self.w).getvalue())


if __name__ == '__main__':
    unittest.main()
