import re
from typing import Tuple, Set, Optional
from unittest import TestCase

from rdflib import RDFS

prefixes_re = re.compile(r"^(?:\s*Prefix\( (.*?) \))", flags=re.MULTILINE)
ontology_re = re.compile(r"Ontology\((.*)\)\s*$", flags=re.MULTILINE+re.DOTALL)


def _parse_output(t: str) -> Tuple[Set[str], str]:
    """ Convert a functional syntax output into a list of prefixes and the ontology definition"""
    prefixes = set()
    m = None
    for m in prefixes_re.finditer(t):
        prefixes.add(m.group(1))
    lastcol = m.regs[0][1] if m is not None else 0
    ontology = ontology_re.findall(t[lastcol:])
    return prefixes, ontology[0] if len(ontology) else ""


def compare_functional_output(expected: str, actual: str, caller: TestCase, msg: Optional[str]) -> None:
    """ Compare expected functional syntax to actual functional syntax taking random order of prefixes into account """
    expected_prefixes, expected_ontology = _parse_output(expected)
    actual_prefixes, actual_ontology = _parse_output(actual)
    if actual_prefixes != expected_prefixes:
        in_actual_only = sorted(list(actual_prefixes - expected_prefixes))
        in_expected_only = sorted(list(expected_prefixes - actual_prefixes))
        if in_actual_only:
            in_actual_list = "\n\t\t".join(sorted(in_actual_only))
            expanded_msg = f"""\n\tUnexpected prefixes:\n\t\t{in_actual_list}\n\t"""
        else:
            expanded_msg = ""
        if in_expected_only:
            # If the only issue is an extra RDFS, let it slide.  Older rdflibs put it in unasked
            if not in_actual_only and len(in_expected_only) == 1 and str(RDFS) in in_expected_only[0]:
                pass
            else:
                in_expected_list = "\n\t\t".join(sorted(in_expected_only))
                expanded_msg += ("\n\t" if expanded_msg else "") + f"""Missing prefixes:\n\t\t{in_expected_list}"""
        if expanded_msg:
            caller.fail(expanded_msg + (msg if msg else ""))
    caller.assertEqual(expected_ontology, actual_ontology, msg)


if __name__ == '__main__':
    inside = """A bunch o
    Inside
    stuff
    Including a "deeply 'embedded Prefix( foo = bar )` as well as a paren and an inner ) Ontology( NOT HERE!!! )
    """

    test = f"""Prefix( xml: = <http://www.w3.org/XML/1998/namespace> )
    Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
    Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
    Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
    Prefix( owl: = <http://www.w3.org/2002/07/owl#> )

    Ontology({inside} )"""

    test2 = """    Prefix( xml: = <http://example.org/xml2#> )
    Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
    Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
    Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
    Prefix( owl: = <http://www.w3.org/2002/07/owl#> )
    Prefix( : = <http://www.w3.org/2002/07/owl#> )"""
    test2_prefixes = {'xsd: = <http://www.w3.org/2001/XMLSchema#>',
                      'owl: = <http://www.w3.org/2002/07/owl#>',
                      'rdfs: = <http://www.w3.org/2000/01/rdf-schema#>',
                      ': = <http://www.w3.org/2002/07/owl#>',
                      'xml: = <http://example.org/xml2#>',
                      'rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#>'}


    class QuickTest(TestCase):
        def test_comparator(self):
            compare_functional_output(test, test, self, "Testing utility failed")

        def test_parser(self):
            self.assertEqual(_parse_output(test2), (test2_prefixes, ""))
            compare_functional_output(test2, test2, self, "Testing utility failed 2")

    qt = QuickTest()
    qt.test_comparator()
    qt.test_parser()
    print("compare_functional_output passes")
