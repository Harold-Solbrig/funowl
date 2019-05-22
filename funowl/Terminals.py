import pyjsg.jsglib as jsg


# String pattern matches used in Functional Owl
# The following productions are taken from ShExJ.py from the ShExJSG project


class LANGTAG(jsg.JSGString):
    pattern = jsg.JSGPattern(r'[a-zA-Z]+(\-([a-zA-Z0-9])+)*')


class HEX(jsg.JSGString):
    pattern = jsg.JSGPattern(r'[0-9]|[A-F]|[a-f]')


class UCHAR(jsg.JSGString):
    pattern = jsg.JSGPattern(r'\\\\u({HEX})({HEX})({HEX})({HEX})|\\\\U({HEX})({HEX})({HEX})({HEX})({HEX})({HEX})({HEX})({HEX})'.format(HEX=HEX.pattern))


class IRIREF(jsg.JSGString):
    pattern = jsg.JSGPattern(r'([^\u0000-\u0020\u005C\u007B\u007D<>"|^`]|({UCHAR}))*'.format(UCHAR=UCHAR.pattern))


class PN_CHARS_BASE(jsg.JSGString):
    pattern = jsg.JSGPattern(r'[A-Z]|[a-z]|[\u00C0-\u00D6]|[\u00D8-\u00F6]|[\u00F8-\u02FF]|[\u0370-\u037D]|[\u037F-\u1FFF]|[\u200C-\u200D]|[\u2070-\u218F]|[\u2C00-\u2FEF]|[\u3001-\uD7FF]|[\uF900-\uFDCF]|[\uFDF0-\uFFFD]|[\U00010000-\U000EFFFF]')


class PN_CHARS_U(jsg.JSGString):
    pattern = jsg.JSGPattern(r'({PN_CHARS_BASE})|_'.format(PN_CHARS_BASE=PN_CHARS_BASE.pattern))


class PN_CHARS(jsg.JSGString):
    pattern = jsg.JSGPattern(r'({PN_CHARS_U})|\-|[0-9]|\\u00B7|[\u0300-\u036F]|[\u203F-\u2040]'.format(PN_CHARS_U=PN_CHARS_U.pattern))


class PNAME_NS(jsg.JSGString):
    pattern = jsg.JSGPattern(r'({PN_CHARS_BASE})((({PN_CHARS})|\.)*({PN_CHARS}))?'.format(PN_CHARS=PN_CHARS.pattern, PN_CHARS_BASE=PN_CHARS_BASE.pattern))


class PNAME_LN(jsg.JSGString):
    pattern = jsg.JSGPattern(r'({PN_CHARS_U})|\-|[0-9]|\\u00B7|[\u0300-\u036F]|[\u203F-\u2040]'.format(PN_CHARS_U=PN_CHARS_U.pattern))


class BLANK_NODE_LABEL(jsg.JSGString):
    pattern = jsg.JSGPattern(r'_:(({PN_CHARS_U})|[0-9])((({PN_CHARS})|\.)*({PN_CHARS}))?'.format(PN_CHARS=PN_CHARS.pattern, PN_CHARS_U=PN_CHARS_U.pattern))