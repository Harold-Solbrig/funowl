import logging
import os
import unittest
from pprint import pprint

from rdflib import Graph

from funowl.converters.functional_converter import to_python
from tests.utils.build_test_harness import ValidationTestCase
from tests.utils.rdf_comparator import compare_rdf, print_triples

logging.getLogger().setLevel(logging.INFO)

OBJECT_INVERSE_ISSUE = "ObjectInverseOf declared on data property - test is bad"
QUESTIONABLE_IRI = "IRI that looks like a BNODE"
DID_NOT_LOAD = "Testcase has issue"


class OWL2ValidationTestCase(ValidationTestCase):
    repo_base = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
    file_suffix = '.func'

    # Starting point in directory
    start_at = 'Bnode2somevaluesfrom.func'

    # True means do exactly one file
    single_file = bool(start_at)

    # Filenames to skip and reason for skipping it
    skip = {'FS2RDF-2Ddomain-2Drange-2Dexpression-2Dar.func': OBJECT_INVERSE_ISSUE,
            'FS2RDF-2Dnegative-2Dproperty-2Dassertion-2Dar.func': OBJECT_INVERSE_ISSUE,
            'TestCase-3AWebOnt-2DequivalentProperty-2D005.func': QUESTIONABLE_IRI,
            'TestCase-3AWebOnt-2Dimports-2D004.func': DID_NOT_LOAD,
            'TestCase-3AWebOnt-2Dimports-2D005.func': DID_NOT_LOAD,
            'TestCase-3AWebOnt-2Dimports-2D006.func': DID_NOT_LOAD,
            'TestCase-3AWebOnt-2Dimports-2D007.func': DID_NOT_LOAD,
            'TestCase-3AWebOnt-2Dimports-2D008.func': DID_NOT_LOAD,
            'TestCase-3AWebOnt-2Dimports-2D013.func': DID_NOT_LOAD,
            'TestCase-3AWebOnt-2Dimports-2D014.func': DID_NOT_LOAD
            }


def validate_owl2(fileloc: str) -> bool:
    logging.info(f"Validating {fileloc}")

    # 1) convert the functional syntax to nn Ontology:
    #    Ontology = f(functional_repr)
    with open(fileloc) as f:
        func_repr = f.read()
    logging.info('\n' + func_repr)
    print(func_repr)
    ontology = to_python(func_repr)

    if not ontology:
        return False

    # 2) determine whether the RDF representation of the Ontology is what is expected
    #    g(f(functional_repr) == RDF
    expected_rdf = Graph()
    expected_rdf.load(fileloc.replace('.func', '.ttl'), format="turtle")
    actual_rdf = Graph()
    ontology.to_rdf(actual_rdf)
    print('='* 40)
    print_triples(expected_rdf)
    print('-'*40)
    print_triples(actual_rdf)
    rslts = compare_rdf(expected_rdf, actual_rdf)
    if rslts:
        print(rslts)
        return False


    # 3) convert the ontology back into functional syntax
    #    functional_repr_prime = f**-1(f(functional_repr))
    print(ontology.to_functional().getvalue())
    ontology_2 = to_python(ontology.to_functional().getvalue())

    # 4) Convert the functional syntax back into an Ontology
    #    Ontology_prime = f(f**-1(f(functional_repr)))

    # 5) Make sure that the RDF representation stll matches
    #    g(f(functional_repr)) == g(f(f**-1(f(functional_repr))
    logging.info('\n' + ontology.to_functional().getvalue())
    return True


OWL2ValidationTestCase.validation_function = validate_owl2

OWL2ValidationTestCase.build_test_harness()

if __name__ == '__main__':
    unittest.main()
