import unittest
from dataclasses import dataclass
from typing import List

from rdflib import RDFS, RDF, XSD, Namespace, OWL

from funowl import Annotation, AnnotationPropertyDomain, AnnotationPropertyRange, AnnotationAssertion, \
    SubAnnotationPropertyOf
from funowl.annotations import Annotatable
from funowl.base.list_support import empty_list_wrapper
from funowl.identifiers import IRI
from funowl.writers import FunctionalWriter
from tests.utils.base import TestBase

a1 = """Annotation(
    Annotation( rdfs:comment "Middle 1" )
    Annotation(
        Annotation( rdfs:comment "Inner" )
        rdfs:label "Middle 2"
    )
    rdfs:comment "Outer"
)"""

a2d = "AnnotationPropertyDomain( rdfs:comment rdfs:Resource )"

a2r = """AnnotationPropertyRange(
    Annotation( rdfs:comment "test" )
    rdfs:comment xsd:string
)"""

a3 = """Foo( 
    Annotation( <http://www.w3.org/2000/01/rdf-schema#comment> "Fine" )
    <http://example.org/ex#a>
    <http://example.org/ex#b>
    <http://example.org/ex#c>
 )"""

EX = Namespace("http://example.org/ex#")


class AnnotationsTestCase(TestBase):

    def test_basic_annotation(self):
        self.assertEqual('Annotation( rdfs:label "This is a test" )',
                         Annotation(RDFS.label, "This is a test").to_functional(self.w).getvalue())

    def test_annotation_IRI(self):
        self.assertEqual("Annotation( rdfs:label rdfs:Resource )",
                         Annotation(RDFS.label, RDFS.Resource).to_functional(self.w).getvalue())

    def test_annotation_anon(self):
        self.assertEqual("Annotation( rdfs:label _:12345 )",
                         Annotation(RDFS.label, '_:12345').to_functional(self.w).getvalue())

    def test_annotation_annotation(self):
        self.assertEqual(a1, Annotation(RDFS.comment, "Outer",
                                        [Annotation(RDFS.comment, "Middle 1"),
                                         Annotation(RDFS.label, "Middle 2",
                                                    [Annotation(RDFS.comment, "Inner")])]).
                         to_functional(self.w).getvalue())

    def test_annotation_domain_range(self):
        self.assertEqual(a2d,
                         AnnotationPropertyDomain(RDFS.comment, RDFS.Resource).to_functional(self.w).getvalue())
        self.w.reset()
        self.assertEqual(a2r,
                         AnnotationPropertyRange(RDFS.comment, XSD.string, [Annotation(RDFS.comment, "test")]).
                         to_functional(self.w).getvalue())

# AnnotationAssertion( rdfs:comment a:Peter "The father of the Griffin family from Quahog." )

    def test_annotation_assertions(self):
        self.assertEqual('AnnotationAssertion( rdfs:comment <http://example.org/ex#peter> '
                         '"The father of the Griffin family from Quahog." )',
                         AnnotationAssertion("rdfs:comment",
                                             EX.peter, "The father of the Griffin family from Quahog.").
                         to_functional(self.w).getvalue())
        self.w.reset()
        self.assertEqual('AnnotationAssertion( <http://example.org/ex#peter> _:abcd rdf:predicate )',
                         AnnotationAssertion(EX.peter, "_:abcd", RDF.predicate).to_functional(self.w).getvalue())

    def test_annotationsubproperty(self):
        self.assertEqual('SubAnnotationPropertyOf( <http://example.org/ex#tag> rdfs:label )',
                         SubAnnotationPropertyOf(EX.tag, RDFS.label).to_functional(self.w).getvalue())

    def test_annotatable_constructor(self):
        """ A single annotation should get transformed into a list by the annotation constructor """
        @dataclass
        class Foo(Annotatable):
            annotations: List[Annotation] = empty_list_wrapper(Annotation)

        a = Annotation(RDFS.comment, "Not a list")
        x = Foo(a)
        self.assertEqual(x.annotations, [a])

    def test_annotatable(self):
        @dataclass
        class Foo(Annotatable):
            props: List[IRI] = empty_list_wrapper(IRI)
            annotations: List[Annotation] = empty_list_wrapper(Annotation)

            def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
                return self.annots(w, lambda: w.iter(self.props, indent=False))

        self.assertEqual("Foo( )", Foo().to_functional(self.w).getvalue())
        f = Foo(annotations=[Annotation(RDFS.comment, "t1")])
        self.w.reset()
        self.assertEqual("""Foo(
    Annotation( rdfs:comment "t1" )
)""", f.to_functional(self.w).getvalue())
        self.w.reset()
        with self.assertRaises(AssertionError):
            f.props += [RDF.type, RDFS.label]
        f.props.extend([RDF.type, RDFS.label])
        f.props.append(OWL.Ontology)
        self.assertEqual("""Foo(
    Annotation( rdfs:comment "t1" )
    rdf:type
    rdfs:label
    owl:Ontology
)""", f.to_functional(self.w).getvalue())
        self.w.reset()
        f.annotations[0].annotations.append(Annotation(RDFS.comment, "This is great"))
        self.assertEqual("""Foo(
    Annotation(
        Annotation( rdfs:comment "This is great" )
        rdfs:comment "t1"
    )
    rdf:type
    rdfs:label
    owl:Ontology
)""", f.to_functional(self.w).getvalue())




if __name__ == '__main__':
    unittest.main()
