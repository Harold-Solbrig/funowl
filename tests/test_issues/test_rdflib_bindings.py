import unittest
from dataclasses import dataclass
from typing import Tuple, Optional, List, Dict

import rdflib
import rdflib_shim

# Make sure the import above works
shimed = rdflib_shim.RDFLIB_SHIM

# Code to evaluate how we can use the rdflib namespace library to manage our namespace behavior.  What we need in
# funowl is:
#  1) Assign multiple prefixes to the same URI including the default ('') prefix
#  2) Map a curie (well - strictly speaking, PNAME_LN as defined in
#      https://www.w3.org/TR/2008/REC-rdf-sparql-query-20080115/#QSynIRI) to a corresponding URI using _any_
#      prefix defined in the Prefixes section
#  3) Map a URI to a curie:
#       a) Using the longest mapped URI possible and
#       b) Using the most recent declared URI mapping in the case of duplicates
#  4) Validate and, when necessary escape URI syntax
#  5) Raise an exception when the same prefix is mapped to two different URIs
#  6) Raise an exception when the following prefixes (from table 2 in the functional spec) are declared
#     rdf, rdfs, xsd, owl
#
#  The closest we can get in rdflib 6.2.0 is
#  1) We NEVER want to use bind(..., replace=False, ...).  Mangled namespaces are not good things.
#  2) We have to preserve ALL prefix/URI mappings, not just the latest
#  3) We have to reject any duplicate prefix declarations
#  2) RDFlib 6.2.0 treats namespaces as a unique dictionary -- you can never have more than one prefix.  This is NOT
#     the behavior we need to implement.
#  3) the namespace_with_bind_override_fix == False appears to replicate some sort of earlier bug that we don't care
#     about.

EX = "http://example.org/ns1#"
EXNS = rdflib.Namespace(EX)
EXURI = rdflib.URIRef(EX)
EX2 = "http://example.org/ns2#"
EX2NS = rdflib.Namespace(EX2)
EX2URI = rdflib.URIRef(EX2)

PRINT_OUTPUT = False                # Print tabular output

using_rdflib_v6 = rdflib.__version__ >= "6.2"
using_rdflib_v5 = rdflib.__version__.startswith("5.0.0")

ignore_prefixes = ['xml', 'rdf', 'rdfs', 'xsd', 'owl']

print(f"===== TESTING RDFLIB VERSION: {rdflib.__version__}")


@unittest.skipUnless(using_rdflib_v5 or using_rdflib_v6, "Tests skipped on unrecognized versions of rdflib")
class RDFLIBNamespaceBindingTestCase(unittest.TestCase):
    """
    Until recently, we have been using the rdflib namespace manager to handle the functional declarations. The 6.x
    release of rdflib, however, has linked the namespace management more tightly with the behavior expected in
    the RDF world.
    """
    @dataclass
    class EvalResult:
        patch: bool             # rdflib.namespace._with_bind_override_fix
        replace: bool
        override: bool
        result: List[Tuple[str, str]]

        @staticmethod
        def hdr() -> str:
            """ Print a table header """
            return "patch\treplace\toverride\tresult\n-----\t-------\t--------\t--------------"

        def __str__(self):
            """ Print the actual result """
            result_str = ' '.join([f"({prefix}:, {ns})" for prefix, ns in self.result])
            return f"{self.patch}\t{self.replace}\t{self.override}\t\t{result_str}"

    @staticmethod
    def print_output(hdr: str) -> None:
        if PRINT_OUTPUT:
            print(f"\n===== {hdr} =====")
            print(RDFLIBNamespaceBindingTestCase.EvalResult.hdr())

    @staticmethod
    def graph_bindings_dict(g: rdflib.Graph) -> Dict[str, str]:
        """ Return non-iggnored graph namespaces as a dictionary """
        return {prefix: str(uri) for prefix, uri in g.namespaces() if prefix not in ignore_prefixes}

    @staticmethod
    def graph_bindings_tuples(g: rdflib.Graph) -> List[Tuple[str, str]]:
        """ Return non-ignored graph namespaces as tuples """
        return [(prefix, uri) for prefix, uri in g.namespaces() if prefix not in ignore_prefixes]

    @staticmethod
    def eval_options(bindings: List[Tuple[Optional[str], str]]) -> List[EvalResult]:
        """ Evaluate how _bindings_ are interpreted using the _replace_, _override_ and _patch_ variables """
        rval = []
        for patch in (True, False):
            for replace in (True, False):
                for override in (True, False):
                    rdflib.namespace._with_bind_override_fix = patch
                    g = rdflib.Graph()
                    for prefix, ns in bindings:
                        g.bind(prefix, ns, override=override, replace=replace)
                    rval.append(
                        RDFLIBNamespaceBindingTestCase.EvalResult(
                            patch, replace, override, RDFLIBNamespaceBindingTestCase.graph_bindings_tuples(g)))
        return rval

    def run_test(self, hdr: str, bindings: List[Tuple[Optional[str], str]]) -> List[EvalResult]:
        """ Run a particular binding test and return the result """
        self.print_output(hdr)
        rslt = self.eval_options(bindings)
        if PRINT_OUTPUT:
            for opt in self.eval_options(bindings):
                print(str(opt))
        return rslt

    def test_decl_default(self):
        """ Test a namespace followed by a default for the same URI """
        rslt = self.run_test("EX: ns1, : ns1", [('EX', EX), (None, EX)])
        for er in rslt:
            # We should have two declarations
            if er.override:
                self.assertEqual(2, len(er.result))
                self.assertEqual({('EX', EXURI), ('', EXURI)}, set(er.result))

    def test_decl_default_rev(self):
        """ Test a default followed by a namespace for the same URI """
        rslt = self.run_test(": ns1, EX: ns1", [(None, EXURI), ('EX', EXURI)])
        for er in rslt:
            # We should have two declarations
            if er.override:
                self.assertEqual(2, len(er.result))
                self.assertEqual({('EX', EXURI), ('', EXURI)}, set(er.result))

    def test_two_namespaces(self):
        """ Test two prefixes with the same URI """
        rslt = self.run_test("EXA: ns1, EXB: ns1", [('EXA', EXURI), ('EXB', EXURI)])
        for er in rslt:
            # We should have two declarations
            if er.override:
                self.assertEqual(2, len(er.result))
                self.assertEqual({('EXA', EXURI), ('EXB', EXURI)}, set(er.result))

    def test_two_diff_namespaces(self):
        """ Test the same prefix with two different URIs

        rdlib 6.2.0 -- if _replace_ and _override_  use last namespace
                       if _replace_ and not _override_ and _patch_ use first namespace
                       if _replace_ and not _override_ and not _patch_ use last namespace
                       if not _replace_ mangle second namespace  (NEVER desirable)
        """
        rslt = self.run_test("EXA: ns1, EXA: ns2", [('EXA', EX), ('EXA', EX2)])
        for er in rslt:
            # We should have two declarations
            if er.replace:
                self.assertEqual(1, len(er.result))
                self.assertEqual({('EXA', EX2URI)}, set(er.result))

    def test_two_defaults(self):
        """
        Test two default declarations for the same URI

        rdlib 6.2.0 -- if _replace_ and _override_ use last namespace
                    -- if _replace_ and not _override_ use first namespace
                    -- if not _replace_ last namespace prefix is "default1" (NEVER desirable)

        """
        rslt = self.run_test(": ns1, : ns2", [(None, EX), (None, EX2)])
        for evalresult in rslt:
            # We should have two declarations
            if evalresult.replace:
                self.assertEqual(1, len(evalresult.result))
                self.assertEqual({('', EX2URI)}, set(evalresult.result))

    def test_three_turtle_namespaces(self):
        """ Examine how rdflib handles two namespaces and a default w/ same URI """

        turtle = """@prefix : <http://example.org/ns1#> .
@prefix NSA: <http://example.org/ns1#> .
@prefix NSB: <http://example.org/ns1#> .
NSA:foo NSB:bar :fee ."""

        # The n3 (turtle) parser maintains its own namespace system to map the above code to the correct URI's
        g = rdflib.Graph()
        g.parse(data=turtle, format="turtle")
        output_ttl = g.serialize(format="turtle")

        # V6 returns a string, V5 returns a bytearray.  This is NOT backwards compatible
        # rdflib_shim takes care of this issue

        # In both versions, only the last version is preserved on output
        self.assertEqual("""@prefix NSB: <http://example.org/ns1#> .

NSB:foo NSB:bar NSB:fee .""", output_ttl.strip())

        nsdict = self.graph_bindings_dict(g)

        # NSB exists in both versions
        self.assertIn("NSB", nsdict)

        # But NSA and default is only available in v5
        if using_rdflib_v5:
            self.assertIn("NSA", nsdict)
            self.assertIn("", nsdict)
            self.assertEqual({'': 'http://example.org/ns1#',
                              'NSA': 'http://example.org/ns1#',
                              'NSB': 'http://example.org/ns1#'}, nsdict)
        elif using_rdflib_v6:
            self.assertNotIn("NSA", nsdict)
            self.assertNotIn("", nsdict)
            self.assertEqual({'NSB': 'http://example.org/ns1#'}, nsdict)

    # All the above are expected to fail in v6 and pass in v5
    test_decl_default.__unittest_expecting_failure__ = using_rdflib_v6
    test_decl_default_rev.__unittest_expecting_failure__ = using_rdflib_v6
    test_two_defaults.__unittest_expecting_failure__ = using_rdflib_v6
    test_two_diff_namespaces.__unittest_expecting_failure__ = using_rdflib_v6
    test_two_namespaces.__unittest_expecting_failure__ = using_rdflib_v6

    @unittest.skipUnless(using_rdflib_v6, "expand_curie is only a v6 function")
    def test_rdflib_v6_expand_curie(self):
        """ Evaluate v6 (only) curie expansion function """
        turtle = """@prefix : <http://example.org/ns1#> .
@prefix NSA: <http://example.org/ns1#> .
@prefix NSB: <http://example.org/ns1#> .
NSA:foo NSB:bar :fee ."""

        # The n3 (turtle) parser maintains its own namespace system to map the above code to the correct URI's
        g = rdflib.Graph()
        g.parse(data=turtle, format="turtle")

        # The good news is that v6 has an _expand_curie_ function:
        self.assertEqual("http://example.org/ns1#test1", str(g.namespace_manager.expand_curie("NSB:test1")))

        # The bad news, however, is 1) It won't work against all curies
        with self.assertRaises(ValueError) as e:
            self.assertEqual("http://example.org/ns1#test1", str(g.namespace_manager.expand_curie("NSA:test1")))
            self.assertIn('Prefix "NSA" not bound to any namespace', str(e))

        # and 2) it doesn't recognize the default namespace, period
        with self.assertRaises(ValueError) as e:
            self.assertEqual("http://example.org/ns1#test1", str(g.namespace_manager.expand_curie(":test1")))
            self.assertIn('Malformed curie argument', str(e))

        # Even if we explicitly add it
        g.bind("", "http://example.org/ns1#", override=True, replace=True)
        self.assertIn("", {prefix: ns for prefix, ns in g.namespaces()})
        with self.assertRaises(ValueError) as e:
            self.assertEqual("http://example.org/ns1#test1", str(g.namespace_manager.expand_curie(":test1")))
            self.assertIn('Malformed curie argument', str(e), "expand_curie simply doesn't recognize defaults")

    def test_rdflib_heisenberg(self):
        """ In which we demonstrate that the act of observing namespaces changes them """

        # If we wait until the end to print the bindings, the default namespace goes away
        g = rdflib.Graph()
        g.bind('', EX)
        g.bind('NSA', EX)
        g.add((EXNS.s1, EXNS.p1, EXNS.o1))
        g.add((EXNS.s2, EXNS.p2, EXNS.o2))
        self.assertEqual("""@prefix NSA: <http://example.org/ns1#> .

NSA:s1 NSA:p1 NSA:o1 .

NSA:s2 NSA:p2 NSA:o2 .""", g.serialize(format="turtle").strip())

        # If we print the bindings in the middle, both namespaces remain
        g = rdflib.Graph()
        g.bind('', EX)
        g.add((EXNS.s1, EXNS.p1, EXNS.o1))
        g.serialize(format="turtle")
        g.bind('NSA', EX)
        g.add((EXNS.s2, EXNS.p2, EXNS.o2))
        self.assertEqual("""@prefix : <http://example.org/ns1#> .
@prefix NSA: <http://example.org/ns1#> .

:s1 :p1 :o1 .

NSA:s2 NSA:p2 NSA:o2 .""", g.serialize(format="turtle").strip())


if __name__ == '__main__':
    unittest.main()
