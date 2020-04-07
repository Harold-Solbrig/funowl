import unittest

from rdflib import Namespace

from funowl import Declaration, Class
from funowl.converters.functional_converter import to_python
from funowl.writers.FunctionalWriter import FunctionalWriter

text = """
Prefix( pizza: = <http://www.co-ode.org/ontologies/pizza/pizza.owl#> )

Ontology( <http://www.co-ode.org/ontologies/pizza> <http://www.co-ode.org/ontologies/pizza/2.0.0>
    Declaration( Class( pizza:American ) )
)
"""
PIZZA = Namespace("http://www.co-ode.org/ontologies/pizza/pizza.owl#")


class DeclarationTestCase(unittest.TestCase):
    def test_base_declaration(self):
        decl = Declaration( Class( PIZZA.American))
        w = FunctionalWriter()
        self.assertEqual("Declaration( Class( <http://www.co-ode.org/ontologies/pizza/pizza.owl#American> ) )",
                         str(decl.to_functional(w)))

    def test_declaration(self):
        parsed = to_python(text)
        actual = str(parsed.to_functional())
        self.assertEqual("""Prefix( xml: = <http://www.w3.org/XML/1998/namespace> )
Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
Prefix( owl: = <http://www.w3.org/2002/07/owl#> )
Prefix( pizza: = <http://www.co-ode.org/ontologies/pizza/pizza.owl#> )

Ontology( <http://www.co-ode.org/ontologies/pizza> <http://www.co-ode.org/ontologies/pizza/2.0.0>
    Declaration( Class( pizza:American ) )
)""", actual)


if __name__ == '__main__':
    unittest.main()
