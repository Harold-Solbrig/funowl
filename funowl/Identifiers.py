""" IRI := fullIRI | abbreviatedIRI """
from dataclasses import dataclass
from typing import Union

from funowl.FunOwlBase import FunOwlChoice
from funowl.GeneralDefinitions import FullIRI, AbbreviatedIRI


@dataclass
class IRI(FunOwlChoice):
    v: Union[FullIRI, AbbreviatedIRI]


class IRIType(IRI):
    def as_owl(self, indent: int = 0) -> str:
        return self.func_name(indent, lambda i1: super(IRIType, self).as_owl(i1))
