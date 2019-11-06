import logging
import os
import unittest
from pprint import pprint

from rdflib import Graph

from funowl.base.rdftriple import TRIPLE
from funowl.converters.functional_converter import to_python
from tests.utils.build_test_harness import ValidationTestCase
from tests.utils.rdf_comparator import compare_rdf, print_triples

logging.getLogger().setLevel(logging.ERROR)

OBJECT_INVERSE_ISSUE = "ObjectInverseOf declared on data property - test is bad"
QUESTIONABLE_IRI = "IRI that looks like a BNODE"
DID_NOT_LOAD = "Testcase has issue"


orig_add = Graph.add


def add(g: Graph, t: TRIPLE) -> None:
    """ Handy debug point for seeing what is going into a graph """
    orig_add(g, t)


class OWL2ValidationTestCase(ValidationTestCase):
    repo_base = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
    file_suffix = '.func'

    # Starting point in directory
    start_at = ''

    # True means do exactly one file
    single_file = bool(start_at)

    # Filenames to skip and reason for skipping it
    skip = { }


def validate_owl2(fileloc: str) -> bool:
    logging.info(f"Validating {fileloc}")

    # 1) convert the functional syntax to nn Ontology:
    #    Ontology = f(functional_repr)
    with open(fileloc) as f:
        func_repr = f.read()
    logging.info('\n===== Input =====\n' + func_repr)
    ontology = to_python(func_repr)

    if not ontology:
        return False

    # 2) determine whether the RDF representation of the Ontology is what is expected
    #    g(f(functional_repr) == RDF
    expected_rdf = Graph()
    expected_rdf.load(fileloc.replace('.func', '.ttl'), format="turtle")
    actual_rdf = Graph()
    actual_rdf.add = lambda t: add(actual_rdf, t)
    ontology.to_rdf(actual_rdf)
    logging.info('\n========== Functional ==========\n' + ontology.to_functional().getvalue())
    logging.info('\n========== RDF =================\n' + actual_rdf.serialize(format="turtle").decode())
    logging.info('\n---------- expected ------------\n' + expected_rdf.serialize(format="turtle").decode())
    rslts = compare_rdf(expected_rdf, actual_rdf)
    if rslts:
        print(rslts)
        return False


    # 3) convert the ontology back into functional syntax
    #    functional_repr_prime = f**-1(f(functional_repr))
    ontology_2 = to_python(ontology.to_functional().getvalue())
    if not ontology_2:
        logging.error(f"Failed to parse emitted functional syntax")
        return False

    # 4) Convert the functional syntax back into an Ontology
    #    Ontology_prime = f(f**-1(f(functional_repr)))
    roundtrip_rdf = Graph()
    ontology_2.to_rdf(roundtrip_rdf)
    logging.info('\n========== Round Trip RDF =================\n' + roundtrip_rdf.serialize(format="turtle").decode())

    # 5) Make sure that the RDF representation stll matches
    #    g(f(functional_repr)) == g(f(f**-1(f(functional_repr))
    rslts = compare_rdf(expected_rdf, roundtrip_rdf)
    if rslts:
        print(rslts)
        return False
    return True


OWL2ValidationTestCase.validation_function = validate_owl2

OWL2ValidationTestCase.build_test_harness()

if __name__ == '__main__':
    unittest.main()
