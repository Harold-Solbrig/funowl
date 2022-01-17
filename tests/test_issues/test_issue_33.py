import sys
import unittest

from rdflib import Namespace

from funowl import EquivalentObjectProperties, Axiom
from funowl.terminals.TypingHelper import isinstance_

EX = Namespace("https://example.org/ex#")


class AxiomInstanceTestCase(unittest.TestCase):

    def test_axiom_instance(self):
        """ Test axiom instance problem """
        x = EquivalentObjectProperties(EX.foo, EX.bar)
        self.assertTrue(isinstance_(x, Axiom) if sys.version_info < (3, 10, 0) else isinstance(x, Axiom))


if __name__ == '__main__':
    unittest.main()
