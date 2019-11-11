import unittest

from funowl.converters.functional_converter import to_python


@unittest.skipIf(False, "NOT Ready for SNOMED")
class SnomedTestCase(unittest.TestCase):
    def test_snomed(self):
        with open('/Users/solbrig/data/terminology/snomedct/'
                  'SnomedCT_InternationalRF2_PRODUCTION_20190731T120000Z/Snapshot/Terminology/snomed.owl') as f:
            d = f.read()
        ontology_doc = to_python(d)
        self.assertTrue(False, "Implement Me")


if __name__ == '__main__':
    unittest.main()
