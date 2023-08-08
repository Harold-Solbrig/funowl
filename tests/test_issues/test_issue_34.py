import sys
import unittest

from rdflib import Namespace

from funowl import EquivalentObjectProperties, Axiom, OntologyDocument, AnnotationAssertion, Literal, AnnotationValue, \
    Prefix
from funowl.terminals.TypingHelper import isinstance_

EX = Namespace("https://example.org/ex#")
SCHEMA = Namespace("http://schema.org/")


class NamespacePollutionTestCase(unittest.TestCase):

    def test_namespace_pollution(self):
        """ Tests https://github.com/Harold-Solbrig/funowl/issues/34 """
        doc = OntologyDocument(ontologyIRI=f"{EX.foo}ontology")
        as_ofn = str(doc)
        assert "schema.org" not in as_ofn
        assert "schema:" not in as_ofn
        assert "brick" not in as_ofn
        x = AnnotationAssertion(SCHEMA.description, EX.foo, AnnotationValue("foo"))
        doc.ontology.axioms.append(x)
        as_ofn = str(doc)
        assert '<http://schema.org/description> <https://example.org/ex#foo>' in as_ofn
        doc.prefixDeclarations.append(Prefix("schema", SCHEMA))
        as_ofn = str(doc)
        assert 'schema:description <https://example.org/ex#foo>' in as_ofn
        doc.prefixDeclarations.append(Prefix("ex", EX))
        as_ofn = str(doc)
        assert 'schema:description ex:foo' in as_ofn



if __name__ == '__main__':
    unittest.main()
