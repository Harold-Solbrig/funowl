import unittest

from rdflib import Graph

from funowl.class_expressions import ObjectHasValue
from funowl.individuals import Individual
from funowl.objectproperty_expressions import ObjectPropertyExpression
from tests.utils.base import TestBase, A


class ClassExpressions(TestBase):

    def test_ObjectIntersectionOf(self):
        pass

    def test_ObjectHasValue(self):
        t = ObjectHasValue(ObjectPropertyExpression(A.foo), Individual(A.bar))
        print(t.to_functional(self.w).getvalue())
        g = Graph()
        t.to_rdf(g)
        print(g.serialize(format="turtle").decode())


if __name__ == '__main__':
    unittest.main()
