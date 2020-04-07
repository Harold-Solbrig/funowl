import os
import unittest
from mmap import mmap, ACCESS_READ
from typing import Any

from funowl import OntologyDocument
from funowl.converters.functional_converter import to_python
from tests import datadir

pizza = os.path.join(datadir, 'pizza.owl')
pizza_fun = os.path.join(datadir, 'pizza.owl.out')


class FunctionalConverterTestCase(unittest.TestCase):
    def verify(self, loc: Any) -> None:
        self.maxDiff = None
        doc = to_python(loc)
        if os.path.exists(pizza_fun):
            with open(pizza_fun) as f:
                expected = f.read()
            self.maxDiff = None
            self.assertEqual(expected, str(doc.to_functional()))
        else:
            with open(pizza_fun, 'w') as f:
                f.write(str(doc.to_functional()))
            self.fail(f"{pizza_fun} written to disc - run test again")

    def test_file(self):
        self.verify(pizza)

    def test_open_file(self):
        with open(pizza, 'r+b') as f:
            self.verify(f)

    def test_open_file_cooked(self):
        with open(pizza) as f:
            self.verify(f)

    def test_string(self):
        with open(pizza) as f:
            txt = f.read()
        self.verify(txt)

    def test_mmem(self):
        with open(pizza) as f:
            self.verify(mmap(f.fileno(), 0, access=ACCESS_READ))

    def test_web_page(self):
        self.verify('https://raw.githubusercontent.com/hsolbrig/funowl/master/tests/data/pizza.owl')


if __name__ == '__main__':
    unittest.main()
