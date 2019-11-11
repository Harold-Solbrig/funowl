import unittest
from mmap import mmap, ACCESS_READ

from funowl.converters.functional_converter import to_python


@unittest.skipIf(True, "NOT Ready for SNOMED")
class SnomedTestCase(unittest.TestCase):
    def test_snomed(self):
        doc = to_python('/Users/solbrig/data/terminology/snomedct/'
                        'SnomedCT_InternationalRF2_PRODUCTION_20190731T120000Z/Snapshot/Terminology/snomed.owl')
        self.assertTrue(False, "Implement Me")

if __name__ == '__main__':
    unittest.main()
