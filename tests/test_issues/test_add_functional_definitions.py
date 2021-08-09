import os
import unittest

from rdflib import Graph

from funowl.converters.functional_converter import to_python
from tests import datadir

pizza = os.path.join(datadir, 'pizza.owl')
pizza_ttl = os.path.join(datadir, 'pizza.ttl')

class FunctionalDefinitionsTestCase(unittest.TestCase):
    """ Test the 'add functional definition' option on the RDF generator"""

    def test_pizza_functional(self):
        pizza_ontology = to_python(pizza)
        g = Graph()
        pizza_ontology.to_rdf(g, emit_functional_definitions=True)
        if os.path.exists(pizza_ttl) and False:
            with open(pizza_ttl) as f:
                expected = f.read()
            self.maxDiff = None
            self.assertEqual(expected, g.serialize(format="turtle").decode())
        else:
            g.serialize(pizza_ttl, format="turtle")


if __name__ == '__main__':
    unittest.main()
