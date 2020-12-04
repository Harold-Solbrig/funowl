import unittest

owlf = """
Prefix(:=<http://ontologies-r.us/clue/>)
Prefix(owl:=<http://www.w3.org/2002/07/owl#>)
Prefix(rdf:=<http://www.w3.org/1999/02/22-rdf-syntax-ns#>)
Prefix(xml:=<http://www.w3.org/XML/1998/namespace>)
Prefix(xsd:=<http://www.w3.org/2001/XMLSchema#>)
Prefix(rdfs:=<http://www.w3.org/2000/01/rdf-schema#>)


Ontology(<http://ontologies-r.us/clue/>

Declaration(Class(<http://ontologies-r.us/clue/Solution>))
Declaration(Class(<http://ontologies-r.us/clue/CompleteSolution>))
Declaration(Class(<http://ontologies-r.us/clue/Room>))

Declaration(ObjectProperty(<http://ontologies-r.us/clue/location>))
SubClassOf(<http://ontologies-r.us/clue/CompleteSolution> <http://ontologies-r.us/clue/Solution>)

SubClassOf(<http://ontologies-r.us/clue/CompleteSolution> ObjectExactCardinality(1 <http://ontologies-r.us/clue/location> <http://ontologies-r.us/clue/Room>))
)
"""

expected = """
@prefix : <http://ontologies-r.us/clue/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

: a owl:Ontology .

:CompleteSolution a owl:Class ;
    rdfs:subClassOf [ a owl:Restriction ;
            owl:onClass :Room ;
            owl:onProperty :location ;
            owl:qualifiedCardinality "1"^^xsd:nonNegativeInteger ],
        :Solution .

:Room a owl:Class .

:Solution a owl:Class .

:location a owl:ObjectProperty .
"""


class ObjectExactCardinalityTestCase(unittest.TestCase):
    def test_owlf_sample(self):
        import os

        from funowl.converters.functional_converter import to_python
        from rdflib import Graph, SKOS, DCTERMS

        clue = to_python(owlf)
        g = Graph()
        clue.to_rdf(g)
        g.bind('skos', SKOS)
        g.bind('dct', DCTERMS)
        owlrdf = g.serialize(format='turtle').decode().strip()
        # print(owlrdf)
        self.assertEqual(expected.strip(), owlrdf)


if __name__ == '__main__':
    unittest.main()
