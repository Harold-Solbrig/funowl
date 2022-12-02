import os
import unittest

from rdflib import Graph

from funowl.converters.functional_converter import to_python
from tests import datadir


class FunctionalToRDFTestCase(unittest.TestCase):
    """ Demo of how one goes about converting functional syntax to RDF """
    def test_fun_to_rdf(self):
        # The functional syntax input can be a string, URL, file loc or open file
        function_pizza = os.path.join(datadir, 'pizza.owl')
        internal_pizza = to_python(function_pizza)

        # Emit the internal representation as an rdflib graph
        g = Graph()
        internal_pizza.to_rdf(g)

        # Serialize the rdflib graph in your favorite format
        turtle_pizza = os.path.join(datadir, 'pizza_out.ttl')
        g.serialize(turtle_pizza)


if __name__ == '__main__':
    unittest.main()
