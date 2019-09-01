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

from rdflib import BNode, URIRef
from rdflib.namespace import is_ncname

from funowl.base.fun_owl_base import FunOwlBase, FunOwlRoot
from funowl.writers.FunctionalWriter import FunctionalWriter
from funowl.terminals.Terminals import PNAME_NS, PNAME_LN, LANGTAG, BLANK_NODE_LABEL, QUOTED_STRING


# Note - super class warning is ok
class NonNegativeInteger(int, FunOwlBase):
    """ a nonempty finite sequence of digits between 0 and 9 """
    def __init__(self, v: int) -> None:
        if not isinstance(v, self.__class__):
            raise TypeError(f"{v}: invalid non-negative integer")

    def _is_valid(self, instance) -> bool:
        try:
            return int(instance) >= 0
        except TypeError:
            return False
        except ValueError:
            return False


class QuotedString(QUOTED_STRING, FunOwlRoot):

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w + ('"' + self.replace('\\', '\\\\').replace('"', '\\"') + '"')


class LanguageTag(LANGTAG, FunOwlRoot):
    """ @ (U+40) followed a nonempty sequence of characters matching the langtag production from [BCP 47] """
    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w + ('@' + str(self))


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

    def _is_valid(self, instance) -> bool:
        # We're going to be a bit loose here -- if we've got a scheme (rfc3987.txt)
        # Also note that we aren't supporting I18N (the 'I' in IRI)
        # TODO: I18N
        return instance is not None and (issubclass(type(instance), FullIRI) or
                                         isinstance(instance, URIRef) or
                                         re.match(r'[a-zA-Z][a-zA-Z-9+-.]*://', str(instance)))

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        v = w.g.namespace_manager.absolutize(str(self))
        return w.concat('<', str(self), '>', sep='')


class PrefixName(PNAME_NS, FunOwlRoot):
    def __new__(cls, v: Optional[str] = None) -> object:
        if v is None:
            v = ''
        elif not isinstance(v, PNAME_NS):
            raise TypeError(f"{v} is not a valid {cls}")
        return PNAME_NS.__new__(cls, v)

    def __init__(self, v: Optional[str] = None) -> None:
        super().__init__(v)
        if not is_ncname(v):
            raise ValueError(f"{v} is not a valid NCNAME according to rdflib")

    """ a finite sequence of characters matching the as PNAME_NS production of [SPARQL] """
    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.concat(str(self), sep='')


class AbbreviatedIRI(PNAME_LN, FunOwlRoot):
    pass
