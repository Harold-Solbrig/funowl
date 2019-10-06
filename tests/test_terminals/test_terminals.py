import unittest
from typing import Any, Type

from funowl.terminals.Terminals import PN_CHARS_BASE, PNAME_LN, HEX, QUOTED_STRING
# class IRIREF(jsg.JSGString):
#     pattern = jsg.JSGPattern(r'([^\u0000-\u0020\u005C\u007B\u007D<>"|^`]|({UCHAR}))*'.format(UCHAR=UCHAR.pattern))
#
#
# class PN_CHARS_BASE(jsg.JSGString):
#     pattern = jsg.JSGPattern(r'[A-Z]|[a-z]|[\u00C0-\u00D6]|[\u00D8-\u00F6]|[\u00F8-\u02FF]|[\u0370-\u037D]|[\u037F-\u1FFF]|[\u200C-\u200D]|[\u2070-\u218F]|[\u2C00-\u2FEF]|[\u3001-\uD7FF]|[\uF900-\uFDCF]|[\uFDF0-\uFFFD]|[\U00010000-\U000EFFFF]')
#
#
# class PN_CHARS_U(jsg.JSGString):
#     pattern = jsg.JSGPattern(r'({PN_CHARS_BASE})|_'.format(PN_CHARS_BASE=PN_CHARS_BASE.pattern))
#
#
# class PN_CHARS(jsg.JSGString):
#     pattern = jsg.JSGPattern(r'({PN_CHARS_U})|\-|[0-9]|\\u00B7|[\u0300-\u036F]|[\u203F-\u2040]'.format(PN_CHARS_U=PN_CHARS_U.pattern))
#
#
# class PNAME_NS(jsg.JSGString):
#     pattern = jsg.JSGPattern(r'({PN_CHARS_BASE})((({PN_CHARS})|\.)*({PN_CHARS}))?'.format(PN_CHARS=PN_CHARS.pattern, PN_CHARS_BASE=PN_CHARS_BASE.pattern))
#
#
# class PNAME_LOCAL(jsg.JSGString):
#     pattern = jsg.JSGPattern(r'(({PN_CHARS_U})|[0-9])((({PN_CHARS})|\.)*({PN_CHARS}))?'.format(PN_CHARS_U=PN_CHARS_U.pattern, PN_CHARS=PN_CHARS.pattern))
#
#
# class BLANK_NODE_LABEL(jsg.JSGString):
#     pattern = jsg.JSGPattern(r'_:(({PN_CHARS_U})|[0-9])((({PN_CHARS})|\.)*({PN_CHARS}))?'.format(PN_CHARS=PN_CHARS.pattern, PN_CHARS_U=PN_CHARS_U.pattern))
#
# class PNAME_LN(jsg.JSGString):
#     pattern = jsg.JSGPattern(r'({PNAME_NS})?:{PNAME_LOCAL}'.format(PNAME_NS=PNAME_NS.pattern, PNAME_LOCAL=PNAME_LOCAL.pattern))
#
# class QUOTED_STRING(jsg.JSGString):
#     pattern = jsg.JSGPattern(r'^".*"$|.*')
#
from tests.utils.base import TestBase


class TerminalsTestCase(TestBase):
    def eval(self, v: Any, t: Type, fail: bool = False, expected: str = None) -> None:
        if not fail:
            self.assertTrue(isinstance(v, t))
            self.assertEqual(str(v) if expected is None else expected, str(t(v)))
        else:
            self.assertFalse(isinstance(v, t))
            with self.assertRaises(ValueError):
                t(v)

    def test_hex(self):
        self.eval('F', HEX)
        self.eval('0', HEX)
        self.eval('G', HEX, fail=True)
        self.eval(0, HEX)

    # def test_uchar(self):
    #     self.eval("\\uFABC", UCHAR)
    #     self.eval("\\U0123ABCF", UCHAR)
    #     self.eval("FABC", UCHAR, fail=True)
    #     self.eval("\\uFAB", UCHAR, fail=True)
    #     self.eval("\\uFABCD", UCHAR, fail=True)
    #     self.eval("\\uFABG", UCHAR, fail=True)

    # TODO: Test the other types

    def test_quoted_string(self):
        self.eval('"I yam a qouted string"', QUOTED_STRING)
        self.eval('I Also count', QUOTED_STRING)
        self.eval('As to "I"', QUOTED_STRING)

    def test_pn_chars_base(self):
        self.assertFalse(isinstance('1', PN_CHARS_BASE))

    def test_pn_ln(self):
        self.assertTrue(isinstance('rdf:cool', PNAME_LN))



if __name__ == '__main__':
    unittest.main()
