# OWL 2 test suite
The OWL 2 Test suite source can be found at https://www.w3.org/2009/11/owl-test/.  [all.rdf](https://www.w3.org/2009/11/owl-test/all.rdf)
contains the complete collection of tests, which we are using strictly for the purpose of functional syntax / RDF conversion
validation.  None of the conversion utilities mentioned in the testing documentation appears to be online, however,
so we have made use of this wonderful [site](http://www.ldf.fi/service/owl-converter/) hosted by [Linked Data Finland](http://www.ldf.fi/).

## Generating the test cases
We begin with a local copy of [a1.rdf](tests/data/all.rdf).  [all_parser.py](tests/test_owl2_test_suite/all_parser.py)
uses `rdflib` to traverse the test library and generates three output files for each test in the [tests/test_owl2_test_suite/data](tests/test_owl2_test_suite/data)
directory:

1) **(testname).func** -- the functional syntax representation of the test.  If the syntax of the actual test case is functional (`http://www.w3.org/2007/OWL/testOntology#normativeSyntax` = `http://www.w3.org/2007/OWL/testOntology#FUNCTIONAL`), the
[converter](http://www.ldf.fi/service/owl-converter/) this is the functional representation in the test case.  If the
syntax of the test case is rdf/xml (`http://www.w3.org/2007/OWL/testOntology#normativeSyntax` = `http://www.w3.org/2007/OWL/testOntology#RDFXML`), 
the [converter](http://www.ldf.fi/service/owl-converter/) is called to transform the RDF into its functional equivalent.
2) **(testname).rdf** -- the rdf/xml representation of the test.  If the syntax of the actual test case is functional, The
[converter](http://www.ldf.fi/service/owl-converter/) is used to generate the rdf/xml equivalent.  *If*, however, the
syntax of the test case is RDF, we perform a two step process:
   1) Convert the [RDF/XML syntax](https://www.w3.org/TR/2012/REC-owl2-mapping-to-rdf-20121211/) into its [functional equivalent](https://www.w3.org/TR/owl2-syntax/)
   2) Convert the result of the conversion back into [RDF](https://www.w3.org/TR/2012/REC-owl2-mapping-to-rdf-20121211/)
  
   This two step process adds any additional type and other inferences that may not have been present in the original
3) **(textname).ttl** -- this is a direct (rdflib) conversion of the [RDF/XML syntax](https://www.w3.org/TR/2012/REC-owl2-mapping-to-rdf-20121211/)
 into the corresponding [Turtle representation](https://www.w3.org/TR/turtle/)
 
 ### Current test case status:
 
 The list below is the output of the latest test case run:
 
    Number of test cases: 493
    Number of conversion errors: 15
	http://owl.semanticweb.org/id/TestCase-3AWebOnt-2Dimports-2D014: Conversion failure
	http://owl.semanticweb.org/id/TestCase-3AWebOnt-2Ddescription-2Dlogic-2D206: Conversion failure
	http://owl.semanticweb.org/id/TestCase-3AWebOnt-2Dmiscellaneous-2D001: Conversion failure
	http://owl.semanticweb.org/id/TestCase-3AWebOnt-2Dmiscellaneous-2D202: Conversion failure
	http://owl.semanticweb.org/id/TestCase-3AWebOnt-2Dimports-2D005: Conversion failure
	http://owl.semanticweb.org/id/TestCase-3AWebOnt-2Dimports-2D007: Conversion failure
	http://owl.semanticweb.org/id/TestCase-3AWebOnt-2Dimports-2D004: Conversion failure
	http://owl.semanticweb.org/id/TestCase-3AWebOnt-2Dmiscellaneous-2D203: Conversion failure
	http://owl.semanticweb.org/id/Rdfbased-2Dsem-2Deqdis-2Ddisclass-2Dirrflxv: None:31:12: rdf:nodeID value is not a valid NCName: _:genid1
	http://owl.semanticweb.org/id/TestCase-3AWebOnt-2DdisjointWith-2D010: None:54:12: rdf:nodeID value is not a valid NCName: _:genid2
	http://owl.semanticweb.org/id/TestCase-3AWebOnt-2Dimports-2D013: Conversion failure
	http://owl.semanticweb.org/id/TestCase-3AWebOnt-2Dimports-2D008: Conversion failure
	http://owl.semanticweb.org/id/TestCase-3AWebOnt-2Dimports-2D006: Conversion failure
	http://owl.semanticweb.org/id/TestCase-3AWebOnt-2DI5.3-2D009: None:36:12: rdf:nodeID value is not a valid NCName: _:genid2
	http://owl.semanticweb.org/id/FS2RDF-2Dnegative-2Dproperty-2Dassertion-2Dar: None:224:12: rdf:nodeID value is not a valid NCName: _:genid9

Four of the test cases are syntactically invalid.  The remaining 11 cause either error 413 or error 500 with the 
conversion tool.  *At some point we might consider using Protege to transform these, but, at the moment we are asumming
that we will have good coverage without them.*

## Running the test suite
The [test_owl2.py](tests/test_owl2_test_suite/test_owl2.py) unit test creates a unit test for every file that ends with 
".func" in the [test directory](tests/test_owl2_test_suite/data).  It evaluates the input using the following steps:
1) Parse the functional representation of the test using the [functional converter](funowl/converters/functional_converter.py).
2) Convert the parsed representation *back* to functional syntax
3) *Re-* parse the output of step 2 
4) Emit the result as RDF
5) Compare the resulting rdf to it's turtle equivalent in the test suite.