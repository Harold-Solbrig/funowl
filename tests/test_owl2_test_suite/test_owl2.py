import logging
import os
import unittest
from typing import Union, Dict

from rdflib import Graph, BNode, URIRef, Literal

from funowl.base.rdftriple import TRIPLE
from funowl.converters.functional_converter import to_python
from tests.utils.build_test_harness import ValidationTestCase
from tests.utils.rdf_comparator import compare_rdf

logging.getLogger().setLevel(logging.WARNING)

OBJECT_INVERSE_ISSUE = "Argument should be declared to be BOTH an Object and Data Property?"
DECIMAL_ISSUE = "Something subtle with 1 and 1.0 decimal"
ONTOLOGY_ANNOTATION_PROBLEM = 'Issue with ontology level annotation -- needs fixing'
XML_LANG_PARSE_ERROR = "Unexplained XML Language"
LOCAL_URI_ISSUE = "funowl doesn't handle document relative URIs"
QUESTIONABLE_IRI = "IRI that looks like a BNODE"
TRIPLE_QUOTED_COMMENT = "Single Quote in Triple Quote Issue"


orig_add = Graph.add

validation_base = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))


def add(g: Graph, t: TRIPLE) -> None:
    """ Handy debug point for seeing what is going into a graph """
    orig_add(g, t)


class OWL2ValidationTestCase(ValidationTestCase):
    repo_base = validation_base
    file_suffix = '.func'

    # Starting point. Copy this from "Validating ..." in output
    start_at = ''

    # True means do exactly one file
    single_file = bool(start_at)

    # Filenames to skip and reason for skipping it
    skip = {
        'FS2RDF/domain/range/expression/ar.func': OBJECT_INVERSE_ISSUE,
        'FS2RDF/literals/ar.func': DECIMAL_ISSUE,
        'FS2RDF/negative/property/assertion/ar.func': OBJECT_INVERSE_ISSUE,
        'TestCase-WebOnt/miscellaneous/204.func': XML_LANG_PARSE_ERROR,
        'TestCase-WebOnt/miscellaneous/203.func': XML_LANG_PARSE_ERROR,
        'TestCase-WebOnt/miscellaneous/202.func': XML_LANG_PARSE_ERROR,
        'TestCase-WebOnt/I5.8/017.func': LOCAL_URI_ISSUE,
        'TestCase-WebOnt/equivalentProperty/005.func': QUESTIONABLE_IRI,
        'TestCase-WebOnt/I5.8/013.func': TRIPLE_QUOTED_COMMENT,
        'TestCase-WebOnt/I5.8/015.func': TRIPLE_QUOTED_COMMENT
    }

    # Stop on the first error
    stop_on_error = False

    # If we're starting at a given file, we'll want more detail
    if start_at:
        logging.getLogger().setLevel(logging.INFO)


# RDF Comparison switch
do_rdf = True


def dump_rdf(g: Graph) -> str:
    bn_map: Dict[BNode, str] = {}

    def nstr(n: BNode) -> str:
        if n not in bn_map:
            bn_map[n] = f"_:b{len(bn_map)}"
        return bn_map[n]

    def n_rdf(n: Union[BNode, URIRef, Literal]) -> str:
        return nstr(n) if isinstance(n, BNode) else n.n3()

    # return '\n'.join(sorted([f"{n_rdf(s)} {n_rdf(p)} {n_rdf(o)} ." for s, p, o in list(g)]))
    return g.serialize(format="turtle").decode()


def validate_owl2(fileloc: str) -> bool:
    print(f"Validating {os.path.relpath(fileloc, validation_base)}")

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
        actual_rdf_graph = Graph()
        actual_rdf_graph.add = lambda t: add(actual_rdf_graph, t)
        ontology_doc.to_rdf(actual_rdf_graph)

        rslts = compare_rdf(expected_rdf, actual_rdf_graph)
        if rslts:
            logging.info('\n========== pass 1 rdf output =================\n' + dump_rdf(actual_rdf_graph))
            logging.info('\n---------- expected rdf ------------\n' + dump_rdf(expected_rdf))
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

    # 5) Test out the to_rdf with the original functional declarations inserted
    #     At the moment, we just make sure everything runs -- we don't actually make sure that what we've got is complete
    rdf_w_functional = Graph()
    ontology_2.to_rdf(rdf_w_functional, emit_functional_definitions=True)
    return True


OWL2ValidationTestCase.validation_function = validate_owl2

OWL2ValidationTestCase.build_test_harness()

if __name__ == '__main__':
    unittest.main()
