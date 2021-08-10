import os
import time
import unittest

from funowl.converters.functional_converter import to_python
from tests import datadir

SKIP_SNOMED_TEST = True


class SnomedTestCase(unittest.TestCase):
    @unittest.skipIf(SKIP_SNOMED_TEST, "This test takes a long time...")
    def test_snomed(self):
        start_time = time.time()
        doc = to_python(os.path.join(datadir, 'ontology-after-conversion.owl'))
        print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    unittest.main()
