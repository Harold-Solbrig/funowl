import unittest

from rdflib import Namespace, URIRef

from funowl import Ontology, DataProperty, OntologyDocument, Declaration, Class, ClassAssertion, DataPropertyAssertion
from funowl.identifiers import IRI


class Issue2TestCase(unittest.TestCase):
    def test_cyclic_issue(self):
        # Create relaMath.owl in functional
        RELA = Namespace("http://sweet.jpl.nasa.gov/2.3/relaMath.owl")
        REPR = Namespace("http://sweet.jpl.nasa.gov/2.3/reprMath.owl")
        o = Ontology(RELA)
        o.imports(REPR)
        o.declarations(DataProperty(RELA['#hasLowerBound']))
        print(str(OntologyDocument(RELA, repr=REPR, ontology=o)))

        # Execute the imports statement
        o.imports(RELA)
        o.declarations(Class(REPR['#Interval']))
        o.axioms.append(DataPropertyAssertion(RELA.hasLowerBound, REPR.NormalizedRange, 0.0))
        o.axioms.append(ClassAssertion(URIRef("Interval"), REPR['#NormalizedRange']))
        print(str(OntologyDocument(RELA, repr=REPR, ontology=o)))


if __name__ == '__main__':
    unittest.main()
