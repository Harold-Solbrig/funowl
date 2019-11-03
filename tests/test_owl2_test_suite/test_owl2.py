import logging
import os
import unittest

from funowl.converters.functional_converter import to_python
from tests.utils.build_test_harness import ValidationTestCase


logging.getLogger().setLevel(logging.INFO)

OBJECT_INVERSE_ISSUE = "ObjectInverseOf declared on data property - test is bad"


class OWL2ValidationTestCase(ValidationTestCase):
    repo_base = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
    file_suffix = '.func'

    # Starting point in directory
    start_at = ''

    # True means do exactly one file
    single_file = bool(start_at)

    # Filenames to skip and reason for skipping it
    skip = {'FS2RDF-2Ddomain-2Drange-2Dexpression-2Dar.func': OBJECT_INVERSE_ISSUE,
            'FS2RDF-2Dnegative-2Dproperty-2Dassertion-2Dar.func': OBJECT_INVERSE_ISSUE,}


def validate_owl2(fileloc: str) -> bool:
    logging.info(f"Validating {fileloc}")

    # 1) convert the functional syntax to nn Ontology:
    #    Ontology = f(functional_repr)
    with open(fileloc) as f:
        func_repr = f.read()
    logging.info('\n' + func_repr)
    ontology = to_python(func_repr)

    if not ontology:
        return False

    # 2) determine whether the RDF representation of the Ontology is what is expected
    #    g(f(functional_repr) == RDF

    # 3) convert the ontology back into functional syntax
    #    functional_repr_prime = f**-1(f(functional_repr))

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
