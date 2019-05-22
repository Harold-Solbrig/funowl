import unittest

from funowl.Terminals import PN_CHARS_BASE


class TerminalsTestCase(unittest.TestCase):
    def test_pn_chars_base(self):
        self.assertFalse(isinstance('1', PN_CHARS_BASE))




if __name__ == '__main__':
    unittest.main()
