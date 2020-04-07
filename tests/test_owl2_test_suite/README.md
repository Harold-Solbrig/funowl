# OWL Test Suite processor

The OWL 2 test suite is only partially operational.  We have been able locate a relatively recent version of the 
test suite, which can be found at [tests/data/all.rdf]().  This directory consists of the following modules:

## [all_parser.py](tests/test_owl2_test_suite/all_parser.py)
This process parses the test suite and then iterates over it loading two output directories:
1) [tests/data/all_test_files]() - this is the unaltered test data in RDF XML (.rdf) or Functional Syntax (.func) files.
This directory can be used to determine whether there were any issues in the conversion process.  
2) [tests/test_owl2_test_suite]() - This carries all of the tests in three formats:  RDF XML (.rdf), Functional Syntax (.func)
and RDF Turtle (.ttl).  The Functional and XML files are used by [tests/test_owl2_test_suite/test_owl2.py]() to validate
the library. The Turtle syntax is there because sometimes it is easier to understand the RDF as Turtle (vs. XML)

## [syntax_converter.py](tests/test_owl2_test_suite/syntax_converter.py)
A single function, `convert`, which uses the [owl conversion service](http://www.ldf.fi/service/owl-converter/) 
published by the [Linked Data Finland](http://www.ldf.fi/) to convert OWL syntaxes.  We use it to generate the functional
format input and to test the resulting RDF output.

## [test_owl2.py](tests/test_owl2_test_wuite/test_owl2.py)
This is the basic test harness.  It creates and executes a unit test for every file with a ".func"
suffix in the [data]() directory and does the following:
1) Parse the functional syntax
2) Serialize the parsed syntax in RDF and compare it to (file).ttl -- this validates the RDF serializer
3) Emit the parsed syntax in Functional Syntax
4) Parse the emitted Functional Syntax
5) Serialize the *re*parsed Functional Syntax in RDF and compare *it* to (file).ttl -- this verifies that the functional
syntax serializer

There are several configuration parameters that can be used with this test:
* `start_at` - line 40 when this was written.  If you have a failing test, you can put the specific test name here.
(Example: `'TestCase-WebOnt/description/logic/504.func'`).  Test names, as a rule, appear as the first line on an
error report.  If this line is non-blank, only this test will be run and a lot of additional diagnostic information will
be generated.
* `stop_on_error` - `True` indicates to stop on the first error.  `False` means run the entire test
* `skip` - A list of files to skip and the reasons they are being skipped.  When this was written, we had 11 skips, for
the following reasons:
    * OBJECT_INVERSE_ISSUE - 


