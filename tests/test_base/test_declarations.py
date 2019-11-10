import unittest

from rdflib import OWL, RDFS, Graph

from funowl.dataproperty_expressions import DataPropertyExpression
from funowl.objectproperty_expressions import ObjectInverseOf, ObjectPropertyExpression
from funowl.annotations import AnnotationProperty
from funowl.declarations import Datatype, ObjectProperty, DataProperty, Declaration
from funowl.class_expressions import Class
from funowl.individuals import NamedIndividual
from tests.utils.base import TestBase, A
from tests.utils.rdf_comparator import compare_rdf

target_rdf = """@prefix a: <http://example.org/a#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

a:Person a owl:Class .

a:Peter a owl:NamedIndividual .

a:SSN a rdfs:Datatype .

rdfs:label a owl:AnnotationProperty .

owl:topDataProperty a owl:DatatypeProperty .

owl:topObjectProperty a owl:ObjectProperty ."""


class DeclarationsTestCase(TestBase):
    def test_func_decls(self):
        Declaration(Datatype(A.SSN)).to_functional(self.wa).br()
        Declaration(Class(A.Person)).to_functional(self.wa).br()
        Declaration(ObjectProperty(OWL.topObjectProperty)).to_functional(self.wa).br()
        Declaration(DataProperty(OWL.topDataProperty)).to_functional(self.wa).br()
        Declaration(AnnotationProperty(RDFS.label)).to_functional(self.wa).br()
        Declaration(NamedIndividual(A.Peter)).to_functional(self.wa).br()
        self.assertEqual("""Declaration( Datatype( a:SSN ) )
Declaration( Class( a:Person ) )
Declaration( ObjectProperty( owl:topObjectProperty ) )
Declaration( DataProperty( owl:topDataProperty ) )
Declaration( AnnotationProperty( rdfs:label ) )
Declaration( NamedIndividual( a:Peter ) )""", self.wa.getvalue())

    def test_rdf_decls(self):
        g = Graph()
        g.bind('a', A)
        g.bind('owl', OWL)

        Declaration(Datatype(A.SSN)).to_rdf(g)
        Declaration(Class(A.Person)).to_rdf(g)
        Declaration(ObjectProperty(OWL.topObjectProperty)).to_rdf(g)
        Declaration(DataProperty(OWL.topDataProperty)).to_rdf(g)
        Declaration(AnnotationProperty(RDFS.label)).to_rdf(g)
        Declaration(NamedIndividual(A.Peter)).to_rdf(g)
        g2 = Graph()
        g2.parse(data=target_rdf, format="turtle")
        msg = compare_rdf(g2, g)
        if msg:
            print(msg)
            self.fail("Graphs do not match")

    def test_inverse_objectProperty(self):
        self.assertEqual('ObjectInverseOf( a:fatherOf )', ObjectInverseOf(A.fatherOf).to_functional(self.wa).getvalue())

    def test_objectpropertyexpression(self):
        ObjectPropertyExpression(A.SSN).to_functional(self.wa).br()
        ObjectPropertyExpression(ObjectInverseOf(A.father)).to_functional(self.wa).br()
        self.assertEqual("""a:SSN
ObjectInverseOf( a:father )""", self.wa.getvalue())

    def test_datapropertyexpression(self):
        DataPropertyExpression(A.SSN).to_functional(self.wa).br()
        self.assertEqual('a:SSN', self.wa.getvalue())


if __name__ == '__main__':
    unittest.main()
