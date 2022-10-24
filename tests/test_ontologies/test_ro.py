import os
import time
import unittest

from funowl.converters.functional_converter import to_python
from tests import datadir


class RelationOntologyTestCase(unittest.TestCase):

    def test_ro(self):
        start_time = time.time()
        doc = to_python(os.path.join(datadir, 'ro.ofn'))
        print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    unittest.main()
