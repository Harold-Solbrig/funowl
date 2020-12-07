import unittest

from funowl.general_definitions import LanguageTag


class LanguageTagTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.save_case_sensitive = LanguageTag.CASE_SENSITIVE

    def tearDown(self) -> None:
        LanguageTag.CASE_SENSITIVE = self.save_case_sensitive

    def test_langtags(self):

        # Test the default setting - case sensitive false
        self.assertEqual('EN', LanguageTag('EN'))

        # Case sensitive checks
        LanguageTag.CASE_SENSITIVE = True
        self.assertEqual('en', LanguageTag('en'))
        self.assertEqual('en-US', LanguageTag('en-US'))
        with self.assertRaises(TypeError) as e:
            LanguageTag('en-us')
        self.assertIn('invalid language tag', str(e.exception))

        # Case insensitive check
        LanguageTag.CASE_SENSITIVE = False
        self.assertEqual('en', LanguageTag('en'))
        self.assertEqual('EN', LanguageTag('EN'))
        self.assertEqual('en-us', LanguageTag('en-us'))
        self.assertEqual('en-US', LanguageTag('en-US'))
        with self.assertRaises(TypeError) as e:
            LanguageTag('aa-bb')
        self.assertIn('invalid language tag', str(e.exception))


if __name__ == '__main__':
    unittest.main()
