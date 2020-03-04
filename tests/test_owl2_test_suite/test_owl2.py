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

OBJECT_INVERSE_ISSUE = "ObjectInverseOf declared on data property - test is bad"
QUESTIONABLE_IRI = "IRI that looks like a BNODE"
DID_NOT_LOAD = "Testcase has issue"
XML_TO_TTL_FAIL = "XML does not load in rdflib"
CONFLICT_WITH_SPEC = "Test case does not appear to match spec"
XML_LANG_PARSE_ERROR = "Unexplained XML Language"
NOT_CONFORMANT_TO_SPEC = "Expected RDF does not match specification"
RDFCOMPARE_BUG = "Bug in RDF comparator"
NEEDS_REVISITING = "Needs hard thinking"

# The issue below is that the test code generates two lists -- one for the thing annotated and a second for the thint
# we generate one list (and we believe that we are correct)
SAME_VS_DUPLICATE_LIST = "Same vs duplicate list"


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
        # 'FS2RDF-2Ddomain-2Drange-2Dexpression-2Dar.func': OBJECT_INVERSE_ISSUE,
        # 'FS2RDF-2Dnegative-2Dproperty-2Dassertion-2Dar.func': OBJECT_INVERSE_ISSUE,
        # 'TestCase-3AWebOnt-2DequivalentProperty-2D005.func': QUESTIONABLE_IRI,
        # 'Rdfbased-2Dsem-2Deqdis-2Ddisclass-2Dirrflxv.func': XML_TO_TTL_FAIL,
        # 'TestCase-3AWebOnt-2DI5.3-2D009.func': XML_TO_TTL_FAIL,
        # 'TestCase-3AWebOnt-2DdisjointWith-2D010.func': XML_TO_TTL_FAIL,
        # 'TestCase-3AWebOnt-2DI5.8-2D017.func': QUESTIONABLE_IRI,
        # 'TestCase-3AWebOnt-2Dmiscellaneous-2D204.func': XML_LANG_PARSE_ERROR,
        # 'Direct_Semantics_Literal_disjoint_from_Thing.func': RDFCOMPARE_BUG,
        # "FS2RDF-2Dpropertychain-2D2-2Dannotated-2Dar.func": SAME_VS_DUPLICATE_LIST,
        # "FS2RDF-2Dontology-2Dannotation-2Dannotation-2Dar.func": NEEDS_REVISITING
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
    return True


OWL2ValidationTestCase.validation_function = validate_owl2

OWL2ValidationTestCase.build_test_harness()

if __name__ == '__main__':
    unittest.main()
