import os
import unittest

from rdflib import Graph

from funowl.converters.functional_converter import to_python
from tests import datadir
from tests.utils.rdf_comparator import compare_rdf

pizza = os.path.join(datadir, 'pizza.owl')
pizza_ttl = os.path.join(datadir, 'pizza.ttl')

class FunctionalDefinitionsTestCase(unittest.TestCase):
    """ Test the 'add functional definition' option on the RDF generator"""

    def test_pizza_functional(self):
        pizza_ontology = to_python(pizza)
        g = Graph()
        pizza_ontology.to_rdf(g, emit_functional_definitions=True)
        if os.path.exists(pizza_ttl):
            rslts = compare_rdf(pizza_ttl, g)
            if rslts:
                print(rslts)
                self.fail(f"Functional definitions have changed -- remove {pizza_ttl} and rerun to overwrite")
        else:
            g.serialize(pizza_ttl, format="turtle")
            self.fail(f"{pizza_ttl} generated -- rerun test")


if __name__ == '__main__':
    unittest.main()
