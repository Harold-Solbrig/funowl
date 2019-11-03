import unittest

from tests.test_owl2_test_suite.syntax_converter import convert


class SyntaxConverterTestCase(unittest.TestCase):
    def test_converter(self):
        print(convert("""<rdf:RDF
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
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
