import unittest

from tests.utils.base import TestBase


class DataPropertyExpressionsTestCase(TestBase):
    @unittest.expectedFailure
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
