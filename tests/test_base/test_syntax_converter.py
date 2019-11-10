import unittest

from tests.test_owl2_test_suite.syntax_converter import convert


class SyntaxConverterTestCase(unittest.TestCase):
    def test_converter(self):
        self.assertEqual("""Prefix(owl:=<http://www.w3.org/2002/07/owl#>)
Prefix(rdf:=<http://www.w3.org/1999/02/22-rdf-syntax-ns#>)
Prefix(xml:=<http://www.w3.org/XML/1998/namespace>)
Prefix(xsd:=<http://www.w3.org/2001/XMLSchema#>)
Prefix(rdfs:=<http://www.w3.org/2000/01/rdf-schema#>)
Prefix(first:=<http://www.w3.org/2002/03owlt/SymmetricProperty/premises001#>)
Prefix(second:=<http://www.w3.org/2002/03owlt/SymmetricProperty/conclusions001#>)


Ontology(
Declaration(ObjectProperty(first:path))
Declaration(NamedIndividual(first:Antwerp))
Declaration(NamedIndividual(first:Ghent))
############################
#   Object Properties
############################

# Object Property: first:path (first:path)

SymmetricObjectProperty(first:path)


############################
#   Named Individuals
############################

# Individual: first:Ghent (first:Ghent)

ObjectPropertyAssertion(first:path first:Ghent first:Antwerp)


)""", convert("""
<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:owl="http://www.w3.org/2002/07/owl#"
    xmlns:first="http://www.w3.org/2002/03owlt/SymmetricProperty/premises001#"
    xmlns:second="http://www.w3.org/2002/03owlt/SymmetricProperty/conclusions001#"
    xml:base="http://www.w3.org/2002/03owlt/SymmetricProperty/premises001" >

    <rdf:Description rdf:about="premises001#Ghent">
        <first:path rdf:resource="premises001#Antwerp"/>
    </rdf:Description>

    <owl:SymmetricProperty rdf:about="premises001#path"/>

</rdf:RDF>"""))


if __name__ == '__main__':
    unittest.main()
