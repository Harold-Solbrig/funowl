import logging
import unittest
from typing import Optional

from rdflib import Namespace

from funowl.writers.FunctionalWriter import FunctionalWriter
from tests import LOGLEVEL
from tests.utils.functional_comparator import compare_functional_output

logging.basicConfig(level=LOGLEVEL)

A = Namespace("http://example.org/a#")


class TestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.w = FunctionalWriter()
        cls.wa = FunctionalWriter()

    def setUp(self) -> None:
        self.w.reset()
        self.wa.reset()

    def assertEqualOntology(self, expected: str, actual: str, msg:Optional[str] = None):
        compare_functional_output(expected, actual, self, msg)

