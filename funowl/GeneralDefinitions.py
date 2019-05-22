"""
nonNegativeInteger := a nonempty finite sequence of digits between 0 and 9
quotedString := a finite sequence of characters in which " (U+22) and \ (U+5C) occur only in pairs of the form \" (U+5C, U+22) and \\ (U+5C, U+5C), enclosed in a pair of " (U+22) characters
languageTag := @ (U+40) followed a nonempty sequence of characters matching the langtag production from [BCP 47]
nodeID := a finite sequence of characters matching the BLANK_NODE_LABEL production of [SPARQL]

fullIRI := an IRI as defined in [RFC3987], enclosed in a pair of < (U+3C) and > (U+3E) characters
prefixName := a finite sequence of characters matching the as PNAME_NS production of [SPARQL]
abbreviatedIRI := a finite sequence of characters matching the PNAME_LN production of [SPARQL]
"""
import re
from typing import Optional

from rdflib import BNode

from funowl.FunOwlBase import FunOwlBase, FunOwlRoot
from funowl.Terminals import PNAME_NS, PNAME_LN, LANGTAG, BLANK_NODE_LABEL


class NonNegativeInteger(int, FunOwlBase):
    """ a nonempty finite sequence of digits between 0 and 9 """
    def __init__(self, v: int) -> None:
        if not isinstance(v, self.__class__):
            raise TypeError(f"{v}: invalid non-negative integer")

    @classmethod
    def _is_valid(cls, instance) -> bool:
        try:
            return int(instance) >= 0
        except TypeError:
            return False
        except ValueError:
            return False


class QuotedString(str, FunOwlBase):
    def __init__(self, v: str) -> None:
        if v is None:
            raise TypeError(f"None value not allowed for type: {type(self)}")


    def as_owl(self, indent: int=0) -> str:
        return self.i(indent) + '"' + self.replace('\\', '\\\\').replace('"', '\\"') + '"'


class LanguageTag(LANGTAG, FunOwlRoot):
    """ @ (U+40) followed a nonempty sequence of characters matching the langtag production from [BCP 47] """
    def as_owl(self, indent: int=0) -> str:
        return self.i(indent) + '@' + str(self)


class NodeID(BLANK_NODE_LABEL, FunOwlRoot):
    """ a finite sequence of characters matching the BLANK_NODE_LABEL production of [SPARQL] """
    def __new__(cls, v: Optional[str] = None) -> object:
        if v is None:
            return BLANK_NODE_LABEL.__new__(cls, BNode().n3())
        elif not isinstance(v, BLANK_NODE_LABEL):
            raise TypeError(f"{v} is not a valid {cls}")
        return BLANK_NODE_LABEL.__new__(cls, v)

    def __init__(self, v: Optional[str] = None) -> None:
        if not isinstance(self, type(self)):
            raise TypeError(f"{v} is not a valid {type(self)}")
        BLANK_NODE_LABEL.__init__(self, self)


class FullIRI(str, FunOwlBase):

    def __init__(self, v: str) -> None:
        if v is None or not self._is_valid(v):
            raise TypeError(f"{v} is not a valid {type(self)}")

    def as_owl(self, indent: int=0) -> str:
        return self.i(indent) + '<' + str(self) + '>'

    def _is_valid(self, instance) -> bool:
        # We're going to be a bit loose here -- if we've got a scheme (rfc3987.txt)
        # Also note that we aren't supporting I18N (the 'I' in IRI)
        # TODO: I18N
        return instance is not None and re.match(r'[a-zA-Z][a-zA-Z-9+-.]*://', str(instance))


class PrefixName(PNAME_NS, FunOwlRoot):
    def __new__(cls, v: Optional[str] = None) -> object:
        if v is None:
            v = ''
        elif not isinstance(v, PNAME_NS):
            raise TypeError(f"{v} is not a valid {cls}")
        return PNAME_NS.__new__(cls, v)

    def __init__(self, v: Optional[str] = None) -> None:
        pass

    """ a finite sequence of characters matching the as PNAME_NS production of [SPARQL] """
    def as_owl(self, indent: int=0) -> str:
        return self.i(indent) + str(self) + ':'


class AbbreviatedIRI(PNAME_LN, FunOwlRoot):
    pass
