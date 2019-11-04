import unittest

from rdflib import RDFS, Namespace

from funowl.annotations import Annotation
from funowl.class_axioms import SubClassOf, EquivalentClasses, DisjointClasses, DisjointUnion, HasKey
from funowl.class_expressions import ObjectIntersectionOf, ObjectSomeValuesFrom
from funowl.dataproperty_expressions import DataPropertyExpression
from funowl.objectproperty_expressions import ObjectPropertyExpression
from funowl.writers.FunctionalWriter import FunctionalWriter
from tests.utils.base import TestBase

SCT = Namespace("http://snomed.info/id/")


class ClassAxiomsTestCase(TestBase):
    def setUp(self) -> None:
        self.sw = FunctionalWriter()
        self.sw.bind(None, SCT)

    def test_subclass_of(self):
        # print(SubClassOf(Annotation(RDFS.comment, "Just a test"), ))
        pass

    def test_equivalentclasses(self):
        self.assertEqual("""EquivalentClasses(
    <http://snomed.info/id/303394007>
    <http://snomed.info/id/45189000>
    <http://snomed.info/id/609096000>
)""", str(EquivalentClasses(SCT['303394007'], SCT['45189000'], SCT['609096000']).to_functional(self.sw)))

        with self.assertRaises(ValueError, msg="at least 2 arguments are required"):
            str(EquivalentClasses( SCT['303394007']).to_functional(self.sw))

        # Taken from SNOMED CT
        self.assertEqual("""EquivalentClasses(
    <http://snomed.info/id/303394007>
        ObjectIntersectionOf(
        <http://snomed.info/id/45189000>
            ObjectSomeValuesFrom( <http://snomed.info/id/609096000>     ObjectIntersectionOf(
            ObjectSomeValuesFrom( <http://snomed.info/id/260686004> <http://snomed.info/id/129397003> )
            ObjectSomeValuesFrom( <http://snomed.info/id/363700003> <http://snomed.info/id/52988006> )
            ObjectSomeValuesFrom( <http://snomed.info/id/405813007> <http://snomed.info/id/69695003> )
    ) )
    )
)""", str(EquivalentClasses(
            SCT['303394007'],
            ObjectIntersectionOf(
                SCT['45189000'],
                ObjectSomeValuesFrom(
                    SCT['609096000'],
                    ObjectIntersectionOf(
                      ObjectSomeValuesFrom(SCT['260686004'], SCT['129397003']),
                      ObjectSomeValuesFrom(SCT['363700003'], SCT['52988006']),
                      ObjectSomeValuesFrom(SCT['405813007'], SCT['69695003']))))).to_functional(self.sw.reset())))

    def test_disjointclasses(self):
        self.assertEqual("""DisjointClasses(
    <http://snomed.info/id/303394007>
    <http://snomed.info/id/45189000>
    <http://snomed.info/id/609096000>
)""", str(DisjointClasses(SCT['303394007'], SCT['45189000'], SCT['609096000']).to_functional(self.sw)))

    def test_disjointunion(self):
        self.assertEqual("""DisjointUnion( <http://snomed.info/id/12345>
    <http://snomed.info/id/303394007>
    <http://snomed.info/id/45189000>
    <http://snomed.info/id/609096000>
)""", str(DisjointUnion(SCT['12345'], SCT['303394007'], SCT['45189000'], SCT['609096000']).
          to_functional(self.sw.reset())))
        with self.assertRaises(ValueError, msg="Have to have at least 2 expressions"):
            DisjointUnion(SCT['12345'], SCT['303394007']).to_functional(self.sw)

    def test_haskey(self):
        self.assertEqual('''HasKey( <http://snomed.info/id/12345> (
    <http://snomed.info/id/23456>
    <http://snomed.info/id/23457>
) (
    <http://snomed.info/id/23458>
    <http://snomed.info/id/23459>
) )''', str(HasKey(SCT['12345'], ObjectPropertyExpression(SCT['23456']), ObjectPropertyExpression(SCT['23457']),
                 DataPropertyExpression(SCT['23458']), DataPropertyExpression(SCT['23459'])).to_functional(self.sw.reset())))


if __name__ == '__main__':
    unittest.main()
