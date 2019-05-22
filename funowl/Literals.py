from dataclasses import dataclass

from funowl.FunOwlBase import FunOwlBase
from funowl.GeneralDefinitions import QuotedString, LanguageTag
from funowl.Identifiers import IRIType


class DataType(IRIType):
    pass


class Literal(QuotedString):
    def __init__(self, v):
        pass

    def _is_valid(self, instance) -> bool:
        return isinstance(instance, str)


@dataclass
class TypedLiteral(Literal):
    literal: QuotedString
    datatype: DataType

    def as_owl(self, indent: int = 0) -> str:
        return self.i(indent) + self.literal.as_owl() + '^^' + self.datatype.as_owl()


class StringLiteralNoLanguage(Literal, QuotedString):
    pass


@dataclass
class StringLiteralWithLanguage(Literal):
    literal: QuotedString
    language: LanguageTag

    def as_owl(self, indent: int = 0) -> str:
        return self.i(indent) + self.literal.as_owl() + self.language.as_owl()
