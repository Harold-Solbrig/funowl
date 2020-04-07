import unittest

from rdflib import Namespace, URIRef

from funowl import Ontology, DataProperty, OntologyDocument, Class, ClassAssertion, DataPropertyAssertion


class Issue2TestCase(unittest.TestCase):
    def test_cyclic_issue(self):
        # Create relaMath.owl in functional
        RELA = Namespace("http://sweet.jpl.nasa.gov/2.3/relaMath.owl")
        REPR = Namespace("http://sweet.jpl.nasa.gov/2.3/reprMath.owl")
        o = Ontology(RELA)
        o.imports(REPR)
        o.declarations(DataProperty(RELA['#hasLowerBound']))
        self.assertEqual("""Prefix( xml: = <http://www.w3.org/XML/1998/namespace> )
Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
Prefix( owl: = <http://www.w3.org/2002/07/owl#> )
Prefix( : = <http://sweet.jpl.nasa.gov/2.3/relaMath.owl> )
Prefix( repr: = <http://sweet.jpl.nasa.gov/2.3/reprMath.owl> )

Ontology( <http://sweet.jpl.nasa.gov/2.3/relaMath.owl>
    Import( <http://sweet.jpl.nasa.gov/2.3/reprMath.owl> )
    Declaration( DataProperty( <http://sweet.jpl.nasa.gov/2.3/relaMath.owl#hasLowerBound> ) )
)""", str(OntologyDocument(RELA, repr=REPR, ontology=o)))

        # Execute the imports statement
        o.imports(RELA)
        o.declarations(Class(REPR['#Interval']))
        o.axioms.append(DataPropertyAssertion(RELA.hasLowerBound, REPR.NormalizedRange, 0.0))
        o.axioms.append(ClassAssertion(URIRef("Interval"), REPR['#NormalizedRange']))
        self.assertEqual("""Prefix( xml: = <http://www.w3.org/XML/1998/namespace> )
Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
Prefix( owl: = <http://www.w3.org/2002/07/owl#> )
Prefix( : = <http://sweet.jpl.nasa.gov/2.3/relaMath.owl> )
Prefix( repr: = <http://sweet.jpl.nasa.gov/2.3/reprMath.owl> )

Ontology( <http://sweet.jpl.nasa.gov/2.3/relaMath.owl>
    Import( <http://sweet.jpl.nasa.gov/2.3/reprMath.owl> )
    Import( <http://sweet.jpl.nasa.gov/2.3/relaMath.owl> )
    Declaration( DataProperty( <http://sweet.jpl.nasa.gov/2.3/relaMath.owl#hasLowerBound> ) )
    Declaration( Class( <http://sweet.jpl.nasa.gov/2.3/reprMath.owl#Interval> ) )
    DataPropertyAssertion( <http://sweet.jpl.nasa.gov/2.3/relaMath.owlhasLowerBound> <http://sweet.jpl.nasa.gov/2.3/reprMath.owlNormalizedRange> "0.0"^^xsd:double )
    ClassAssertion( <Interval> <http://sweet.jpl.nasa.gov/2.3/reprMath.owl#NormalizedRange> )
)""", str(OntologyDocument(RELA, repr=REPR, ontology=o)))


if __name__ == '__main__':
    unittest.main()
