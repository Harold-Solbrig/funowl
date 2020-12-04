import os
import time
import unittest

from funowl.converters.functional_converter import to_python
from tests import datadir


class SnomedTestCase(unittest.TestCase):
    def test_snomed(self):
        start_time = time.time()
        doc = to_python(os.path.join(datadir, 'ontology-after-conversion.owl'))
        print("--- %s seconds ---" % (time.time() - start_time))
        self.assertTrue(False, "Implement Me")

if __name__ == '__main__':
    unittest.main()
