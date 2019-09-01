import logging
import unittest

from rdflib import Namespace

from funowl.writers.FunctionalWriter import FunctionalWriter
from tests import LOGLEVEL

logging.basicConfig(level=LOGLEVEL)

A = Namespace("http://example.org/a#")


class TestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.w = FunctionalWriter()
        cls.wa = FunctionalWriter()
        cls.wa.bind('a', A)

    def setUp(self) -> None:
        self.w.reset()
        self.wa.reset()
