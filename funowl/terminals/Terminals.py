
# String pattern matches used in Functional Owl
# The following productions are taken from ShExJ.py from the ShExJSG project
from typing import Union, Any

from funowl.terminals.Patterns import String, Pattern


class HEX(String):
    pattern = Pattern(r'[0-9]|[A-F]|[a-f]')
    python_type = Union[int, str]


class UCHAR(String):
    pattern = Pattern(r'\\\\u({HEX})({HEX})({HEX})({HEX})|\\\\U({HEX})({HEX})({HEX})({HEX})({HEX})({HEX})({HEX})({HEX})'.format(HEX=HEX.pattern))


class IRIREF(String):
    pattern = Pattern(r'([^\u0000-\u0020\u005C\u007B\u007D<>"|^`]|({UCHAR}))*'.format(UCHAR=UCHAR.pattern))


class PN_CHARS_BASE(String):
    pattern = Pattern(r'[A-Z]|[a-z]|[\u00C0-\u00D6]|[\u00D8-\u00F6]|[\u00F8-\u02FF]|[\u0370-\u037D]|[\u037F-\u1FFF]|[\u200C-\u200D]|[\u2070-\u218F]|[\u2C00-\u2FEF]|[\u3001-\uD7FF]|[\uF900-\uFDCF]|[\uFDF0-\uFFFD]|[\U00010000-\U000EFFFF]')


class PN_CHARS_U(String):
    pattern = Pattern(r'({PN_CHARS_BASE})|_'.format(PN_CHARS_BASE=PN_CHARS_BASE.pattern))


class PN_CHARS(String):
    pattern = Pattern(r'({PN_CHARS_U})|\-|[0-9]|\\u00B7|[\u0300-\u036F]|[\u203F-\u2040]'.format(PN_CHARS_U=PN_CHARS_U.pattern))


class PNAME_NS(String):
    pattern = Pattern(r'({PN_CHARS_BASE})((({PN_CHARS})|\.)*({PN_CHARS}))?'
                      .format(PN_CHARS=PN_CHARS.pattern, PN_CHARS_BASE=PN_CHARS_BASE.pattern))

class OPT_PNAME_NS(String):
    pattern = Pattern(r'(({PN_CHARS_BASE})((({PN_CHARS})|\.)*({PN_CHARS}))?)?'
                      .format(PN_CHARS=PN_CHARS.pattern, PN_CHARS_BASE=PN_CHARS_BASE.pattern))

class PNAME_LOCAL(String):
    pattern = Pattern(r'(({PN_CHARS_U})|[0-9])((({PN_CHARS})|\.)*({PN_CHARS}))?'.format(PN_CHARS_U=PN_CHARS_U.pattern, PN_CHARS=PN_CHARS.pattern))


class BLANK_NODE_LABEL(String):
    pattern = Pattern(r'_:(({PN_CHARS_U})|[0-9])((({PN_CHARS})|\.)*({PN_CHARS}))?'.format(PN_CHARS=PN_CHARS.pattern, PN_CHARS_U=PN_CHARS_U.pattern))


class PNAME_LN(String):
    pattern = Pattern(r'({PNAME_NS})?:{PNAME_LOCAL}'.format(PNAME_NS=PNAME_NS.pattern, PNAME_LOCAL=PNAME_LOCAL.pattern))


class QUOTED_STRING(String):
    pattern = Pattern(r'^".*"$|.*')
    python_type = Any
