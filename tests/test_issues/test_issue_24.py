import os
import unittest
from contextlib import redirect_stderr
from io import StringIO

from funowl.converters.functional_converter import to_python
from tests import datadir, SKIP_LONG_TESTS


class OBILangTagTestCase(unittest.TestCase):

    @unittest.skipIf(SKIP_LONG_TESTS, "obi image must be present to run this")
    def test_obi_issue(self):
        # To run this test:
        #   a) Download an image of https://bioportal.bioontology.org/ontologies/OBI from the owl link
        #   b) Use protege to load the downloaded image (ext.owl) and save it in OWL functional syntax (obi.owlf.owl)
        #   c) Save the output in tests/data/obi.owlf
        txt = StringIO()
        with redirect_stderr(txt):
            with open(os.path.join(datadir, 'obi.owlf')) as f:
                owl = to_python(f.read())
        print(str(owl)[-1024:])


if __name__ == '__main__':
    unittest.main()
