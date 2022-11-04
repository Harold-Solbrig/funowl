import unittest
from dataclasses import dataclass
from typing import Tuple, Optional, List

import rdflib

# Code to evaluate how we can use the rdflib namespace library to manage our namespace behavior.  What we want is the
# following
#  1) Assignment of the same prefix to two different namespaces is a) an error?  b) an override?
#  2) Assignment of the same namespace to two (or more) different prefixes is just and should be accepted.
#
#  The closest we can get in rdflib 6.2.0 is
#  1) We NEVER want to use replace=False.  Mangled namespaces are never desirable
#  2) RDFlib 6.2.0 treats namespaces as a unique dictionary -- you can never have more than one prefix.  This is NOT
#     the behavior we need to implement.
#  3) the namespace_with_bind_override_fix == False appears to replicate some sort of earlier bug that we don't care
#     about.

EX = "http://example.org/ns1#"
EX2 = "http://example.org/ns2#"

PRINT_OUTPUT = True                # Print tabular output

# @unittest.skipIf(rdflib.__version__.startswith("6.2.0"), "rdflib 6.2 doesn't allow dup namespaces")
# @unittest.skipIf(rdflib.__version__.startswith("6.1"), "rdflib 6.1 adds a whole mess of unwanted namespaces")
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
            return "patch\treplace\toverride\tresult\n-----\t-------\t--------\t--------------"

        def __str__(self):
            result_str = ' '.join([f"({prefix}:, {ns})" for prefix, ns in self.result])
            return f"{self.patch}\t{self.replace}\t{self.override}\t\t{result_str}"

    @staticmethod
    def print_output(hdr: str) -> None:
        if PRINT_OUTPUT:
            print(f"\n===== {hdr} =====")
            print(RDFLIBNamespaceBindingTestCase.EvalResult.hdr())

    @staticmethod
    def eval_options(bindings: List[Tuple[Optional[str], str]]) -> List[EvalResult]:
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
                            patch, replace, override,
                            [(prefix, str(ns)) for prefix, ns in g.namespaces() if not prefix or prefix.startswith('EX')]))
        return rval

    def run_test(self, hdr: str, bindings: List[Tuple[Optional[str], str]]) -> List[EvalResult]:
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
                self.assertEqual({('EX', EX), ('', EX)}, set(er.result))

    def test_decl_default_rev(self):
        """ Test a default followed by a namespace for the same URI """
        rslt = self.run_test(": ns1, EX: ns1", [(None, EX), ('EX', EX)])
        for er in rslt:
            # We should have two declarations
            if er.override:
                self.assertEqual(2, len(er.result))
                self.assertEqual({('EX', EX), ('', EX)}, set(er.result))

    def test_two_namespaces(self):
        """ Test two prefixes with the same URI """
        rslt = self.run_test("EXA: ns1, EXB: ns1", [('EXA', EX), ('EXB', EX)])
        for er in rslt:
            # We should have two declarations
            if er.override:
                self.assertEqual(2, len(er.result))
                self.assertEqual({('EXA', EX), ('EXB', EX)}, set(er.result))

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
                self.assertEqual({('EXA', EX2)}, set(er.result))

    def test_two_defaults(self):
        """
        Test two default declarations for the same URI

        rdlib 6.2.0 -- if _replace_ and _override_ use last namespace
                    -- if _replace_ and not _override_ use first namespace
                    -- if not _replace_ last namespace prefix is "default1" (NEVER desirable)

        """
        rslt = self.run_test(": ns1, : ns2", [(None, EX), (None, EX2)])
        for er in rslt:
            # We should have two declarations
            if er.replace:
                self.assertEqual(1, len(er.result))
                self.assertEqual({('', EX2)}, set(er.result))


if __name__ == '__main__':
    unittest.main()
