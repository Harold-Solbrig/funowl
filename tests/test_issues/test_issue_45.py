import os
import unittest
from io import StringIO

from funowl.converters.functional_converter import to_python
from tests import datadir


class CRTestCase(unittest.TestCase):

    """ Test issue_45 - error thrown if literals contain carriage returns """
    def test_cr_issue(self):
        owl = None
        with open(os.path.join(datadir, 'cr.ofn.txt')) as f:
            owl = to_python(f.read())
        self.assertTrue(str(owl.ontology.annotations[1].value.v).startswith("\n  This ontology partially"))


if __name__ == '__main__':
    unittest.main()
