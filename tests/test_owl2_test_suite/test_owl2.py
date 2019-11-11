import logging
import os
import unittest

from rdflib import Graph

from funowl.base.rdftriple import TRIPLE
from funowl.converters.functional_converter import to_python
from tests.utils.build_test_harness import ValidationTestCase
from tests.utils.rdf_comparator import compare_rdf

logging.getLogger().setLevel(logging.WARNING)

OBJECT_INVERSE_ISSUE = "ObjectInverseOf declared on data property - test is bad"
QUESTIONABLE_IRI = "IRI that looks like a BNODE"
DID_NOT_LOAD = "Testcase has issue"
XML_TO_TTL_FAIL = "XML does not load in rdflib"


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
    skip = {
        'FS2RDF-2Ddomain-2Drange-2Dexpression-2Dar.func': OBJECT_INVERSE_ISSUE,
        'FS2RDF-2Dnegative-2Dproperty-2Dassertion-2Dar.func': OBJECT_INVERSE_ISSUE,
        'TestCase-3AWebOnt-2DequivalentProperty-2D005.func': QUESTIONABLE_IRI,
        'Rdfbased-2Dsem-2Deqdis-2Ddisclass-2Dirrflxv.func': XML_TO_TTL_FAIL,
        'TestCase-3AWebOnt-2DI5.3-2D009.func': XML_TO_TTL_FAIL,
        'TestCase-3AWebOnt-2DdisjointWith-2D010.func': XML_TO_TTL_FAIL,
        'TestCase-3AWebOnt-2DI5.8-2D017.func': QUESTIONABLE_IRI
    }

    # Stop on the first error
    stop_on_error = False

    # If we're starting at a given file, we'll want more detail
    if start_at:
        logging.getLogger().setLevel(logging.INFO)


# RDF Comparison switch
do_rdf = True


def validate_owl2(fileloc: str) -> bool:
    print(f"Validating {os.path.basename(fileloc)}")

    # 1) convert the functional syntax to nn Ontology:
    #    Ontology = f(functional_repr)
    with open(fileloc) as f:
        func_repr = f.read()
    logging.info('\n===== Original Input =====\n' + func_repr)
    ontology_doc = to_python(func_repr)

    if not ontology_doc:
        return False
    logging.info('\n===== Pass 1 Output =====\n' + str(ontology_doc.to_functional()))

    # 2) determine whether the RDF representation of the Ontology is what is expected
    #    g(f(functional_repr) == RDF
    if do_rdf:
        expected_rdf = Graph()
        expected_rdf.load(fileloc.replace('.func', '.ttl'), format="turtle")
        actual_rdf = Graph()
        actual_rdf.add = lambda t: add(actual_rdf, t)
        ontology_doc.to_rdf(actual_rdf)

        rslts = compare_rdf(expected_rdf, actual_rdf)
        if rslts:
            logging.info('\n========== pass 1 rdf output =================\n' + actual_rdf.serialize(format="turtle").decode())
            logging.info('\n---------- expected rdf ------------\n' + expected_rdf.serialize(format="turtle").decode())
            print(rslts)
            return False


    # 3) convert the ontology back into functional syntax
    #    functional_repr_prime = f**-1(f(functional_repr))
    ontology_2 = to_python(ontology_doc.to_functional().getvalue())
    if not ontology_2:
        logging.error(f"Failed to parse emitted functional syntax")
        return False
    logging.info('\n===== Pass 2 Output =====\n' + str(ontology_2.to_functional()))

    # 4) Convert the functional syntax back into an Ontology
    #    Ontology_prime = f(f**-1(f(functional_repr)))
    if do_rdf:
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
