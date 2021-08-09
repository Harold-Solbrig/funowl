"""
Literal := typedLiteral | stringLiteralNoLanguage | stringLiteralWithLanguage
typedLiteral := lexicalForm '^^' Datatype
lexicalForm := quotedString
stringLiteralNoLanguage := quotedString
stringLiteralWithLanguage := quotedString languageTag
"""
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Optional, Union, Any, Tuple, ClassVar

import rdflib
from rdflib import Graph, Literal
from rdflib.namespace import RDFS, XSD, RDF
from rdflib.plugins.parsers.notation3 import BadSyntax
from rdflib.term import Node

from funowl.base.cast_function import exclude
from funowl.base.fun_owl_base import FunOwlBase
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.writers.FunctionalWriter import FunctionalWriter
from funowl.general_definitions import QuotedString, LanguageTag
from funowl.identifiers import IRI


@dataclass
class Datatype(IRI):
    rdf_type = RDFS.Datatype


class StringLiteralNoLanguage(QuotedString):
    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> Literal:
        return rdflib.Literal(self)


@dataclass
class TypedLiteral(FunOwlBase):
    literal: Union[int, float, bool, date, time, datetime, rdflib.Literal, StringLiteralNoLanguage]
    datatype: Optional[Datatype] = None

    def __init__(self,
                 literal: Union[int, float, bool, date, time, datetime, rdflib.Literal, StringLiteralNoLanguage],
                 datatype: Optional[Datatype] = None) -> None:
        """
        TypedLiteral can be forced (type specified) or implicit
        :param literal: Literal
        :param datatype: Data type or None if it is to be coputed
        """
        if issubclass(type(literal), TypedLiteral):
            self.literal = literal.literal
            self.datatype = literal.datatype
        elif datatype is not None:
            self.literal = StringLiteralNoLanguage(literal)
            self.datatype = datatype if issubclass(type(datatype), Datatype) else Datatype(datatype)
        elif isinstance(literal, (int, float, bool, date, time, datetime, rdflib.Literal)):
            if not isinstance(literal, rdflib.Literal):
                literal = rdflib.Literal(literal)
            self.literal = StringLiteralNoLanguage(literal.value)
            self.datatype = literal.datatype if literal.datatype else XSD.string
        else:
            raise ValueError(f"Unknown TypedLiteral constructor: {literal}^^{datatype}")

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.concat(self.literal, '^^', self.datatype)

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> rdflib.Literal:
        return rdflib.Literal(self.literal, datatype=IRI(str(self.datatype)).to_rdf(g, emit_type_arc=emit_type_arc))

    def __str__(self) -> str:
        return str(self.literal) + '^^' + str(self.datatype)

    def _is_valid(cls: Union[type, Tuple[type, ...]], instance) -> bool:
        if issubclass(type(instance), cls) or isinstance(instance, (int, float, bool, date, time, datetime)):
            return True
        elif isinstance(instance, rdflib.Literal):
            return instance.datatype and instance.datatype != XSD.string
        elif isinstance(instance, str):
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
    literal: Union[StringLiteralNoLanguage, str, rdflib.Literal] = exclude([str, rdflib.Literal])
    language: Optional[Union[LanguageTag, str]] = exclude([str], default=None)

    def __init__(self, literal: Union[StringLiteralNoLanguage, "StringLiteralWithLanguage", str, rdflib.Literal],
                 language: Optional[Union[LanguageTag, str]] = None) -> None:
        if isinstance(literal, rdflib.Literal):
            self.literal = literal.value
            self.literal = literal.language
        elif isinstance(literal, StringLiteralWithLanguage):
            self.literal = literal.literal
            self.language = literal.language
        else:
            assert language, "Language must be supplied"
            self.literal = StringLiteralNoLanguage(str(literal))
            self.language = language

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.concat(self.literal, self.language)

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> rdflib.Literal:
        return rdflib.Literal(self.literal, lang=str(self.language))

    def __str__(self) -> str:
        return str(self.literal) + '@' + str(self.language)


@dataclass
class Literal(FunOwlChoice):
    # Warning: StringLiteralNoLanguage has to be last in this list
    v: Union[TypedLiteral, StringLiteralWithLanguage, StringLiteralNoLanguage, int, float, bool, date, datetime, time]

    def set_v(self, value: Any) -> bool:
        """ Default setter -- can be invoked from more elaborate coercion routines
        :param value: value to set
        :return: True if v was set
        """
        if isinstance(value, (int, float, bool, date, datetime, time)):
            self.v = value
            return True
        else:
            return super().set_v(value)

    def __setattr__(self, key, value):
        if key != 'v':
            super().__setattr__(key, value)
        elif isinstance(value, (int, float, bool, date, datetime, time)):
            cl = rdflib.Literal(value)
            super().__setattr__('v', TypedLiteral(cl.value, cl.datatype))
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
        """
        Parse a stringified representation of V to get a Literal in return
        :param v: value to convert to literal
        :return: Literal representation, if possible
        """
        if isinstance(v, rdflib.Literal):
            return v
        if isinstance(v, (int, float, bool, date, datetime, time)):
            return rdflib.Literal(v)
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
        return Literal._to_n3(instance) is not None

