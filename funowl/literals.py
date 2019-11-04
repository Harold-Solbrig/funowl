"""
Literal := typedLiteral | stringLiteralNoLanguage | stringLiteralWithLanguage
typedLiteral := lexicalForm '^^' Datatype
lexicalForm := quotedString
stringLiteralNoLanguage := quotedString
stringLiteralWithLanguage := quotedString languageTag
"""
from dataclasses import dataclass
from typing import Optional, Union, Any, Tuple

import rdflib
from rdflib import Graph, Literal
from rdflib.namespace import RDFS, XSD, RDF
from rdflib.plugins.parsers.notation3 import BadSyntax
from rdflib.term import Node

from funowl.base.fun_owl_base import FunOwlBase
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.writers.FunctionalWriter import FunctionalWriter
from funowl.general_definitions import QuotedString, LanguageTag
from funowl.identifiers import IRI


@dataclass
class Datatype(IRI):
    rdf_type = RDFS.Datatype


class StringLiteralNoLanguage(QuotedString):
    def to_rdf(self, g: Graph) -> Literal:
        return rdflib.Literal(self)


@dataclass
class TypedLiteral(FunOwlBase):
    literal: StringLiteralNoLanguage
    datatype: Datatype

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.concat(self.literal, '^^', self.datatype)

    def __str__(self) -> str:
        return str(self.literal) + '^^' + str(self.datatype)

    def _is_valid(cls: Union[type, Tuple[type, ...]], instance) -> bool:
        if issubclass(type(instance), cls):
            return True
        if isinstance(instance, str):
            l = Literal._to_n3(instance)
            return l.datatype and l.datatype != XSD.string
        return False

    @classmethod
    def _parse_input(cls, v: Any) -> Tuple[Any]:
        if issubclass(type(v), cls):
            return (v.literal, v.datatype)
        l = Literal._to_n3(v)
        return (l.value, l.datatype)


@dataclass(init=False)
class StringLiteralWithLanguage(FunOwlBase):
    literal: StringLiteralNoLanguage
    language: LanguageTag

    def __init__(self, literal: Any, language: Union[LanguageTag, str]) -> None:
        self.literal = StringLiteralNoLanguage(str(literal))
        self.language = language

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.concat(self.literal, self.language)

    def __str__(self) -> str:
        return str(self.literal) + '@' + str(self.language)


@dataclass
class Literal(FunOwlChoice):
    # Warning: StringLiteralNoLanguage has to be last in this list
    v : Union[TypedLiteral, StringLiteralWithLanguage, StringLiteralNoLanguage]

    def __setattr__(self, key, value):
        if key != 'v':
            super().__setattr__(key, value)
        elif isinstance(value, str) or not self.set_v(value):
            l = Literal._to_n3(value)
            if l is None:
                raise ValueError(f"Literal: {value} is not a valid literal")
            if l.language:
                vv = StringLiteralWithLanguage(l.value, l.language)
            elif l.datatype and l.datatype != XSD.string:
                vv = TypedLiteral(l.value, l.datatype)
            else:
                vv = StringLiteralNoLanguage(l.value)
            super().__setattr__('v', vv)

    @staticmethod
    def _to_n3(v: Any) -> Optional[rdflib.Literal]:
        if not isinstance(v, str):
            v = str(v)
        v = v.replace("\n", "\\n")

        # Add quotes if necessary
        if v[0] not in ['"', "'"]:
            v = '"' + v + '"'
        # Create a turtle triple to use the n3 parser
        stmt = f'@prefix xsd: <http://www.w3.org/2001/XMLSchema#> . xsd:f a {v} .'
        g = Graph()
        try:
            g.parse(data=stmt, format="turtle")
        except BadSyntax:
            pass
        # Probably a bug in rdflib, but "n"^^xsd.integer produces this error
        except IndexError:
            pass
        l = g.value(XSD.f, RDF.type)
        if l is not None:
            if not isinstance(l, rdflib.Literal) or l.value is None:
                l = None
        return l

    def _is_valid(cls, instance) -> bool:
        return bool(Literal._to_n3(instance))

