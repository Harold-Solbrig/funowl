import logging
import re
from dataclasses import dataclass
from pprint import pformat
from typing import Union, List, Tuple, Match, cast, Optional

import rdflib

import funowl
from funowl import Ontology, Prefix, Annotation
from funowl.base.fun_owl_base import FunOwlBase
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.literals import TypedLiteral, StringLiteralWithLanguage, StringLiteralNoLanguage

ontology_re = re.compile(r'\s*Ontology\s*\((.*)\s*\)\s*$', flags=re.DOTALL)

func = """Prefix (  := <http://example.org/> )
Prefix(xsd:=<http://www.w3.org/2001/XMLSchema#>)
Ontology(
  Declaration(NamedIndividual(:a))
  Declaration(DataProperty(:dp))
  Declaration(Class(:A))
  SubClassOf(:A 
    DataHasValue(:dp "2007-10-08T20:44:11.656+01:00"^^xsd:dateTime)) 
  SubClassOf(:A 
    DataAllValuesFrom(:dp DatatypeRestriction(
      xsd:dateTime 
      xsd:minInclusive "2008-07-08T20:44:11.656+01:00"^^xsd:dateTime 
      xsd:maxInclusive "2008-10-08T20:44:11.656+01:00"^^xsd:dateTime)
    )
  ) 
  ClassAssertion(:A :a)
)"""

# Target:
# Prefix(' := <....>')
# Ontology(
#     Declaration(NamedIndividual(":a")), Declaration(Dataproperty(":dp"))
# )
#
# Generic Syntax:
#   Function ( args )
#   args = FunctIon | literal | embedded list
#   literal = URIRef | Literal
#   embedded list FunctIon|embedded list "(" args ")"

# 1: Function '('
function_re = re.compile(r'([A-Z][A-Za-z]+)\s*\(', flags=re.DOTALL)
# 1: Prefix ':=' 2: URI
prefix_re = re.compile(r'(\S*):\s*=\s*(\S*)', flags=re.DOTALL)
# '<' 1:uri '>
abs_uri = re.compile(r'<([^>]+)>', flags=re.DOTALL)
# 1: rel-url
rel_uri = re.compile(r'(([A-Za-z_]).*?:\S+)', flags=re.DOTALL)
# 1: literal
literal_re = re.compile(r'("[^"]*"|\S+)', flags=re.DOTALL)
# 1: lang
literal_lang = re.compile(r'@(\S+)')
# 1: datatype
literal_datatype = re.compile(r'\^\^(\S+)')
# '(' 1:
nested_re = re.compile(r'\(\s*(.+\s*\))', flags=re.DOTALL)
# TODO: Where is this defined and how do we deal with different EOL's?
comments_re = re.compile(r'#[^\n]*\n?', flags=re.DOTALL)


@dataclass
class OWLFunc:
    """
    A function consists of a function name and a list consisting of owl functions, rdflib literals or lists of both """
    function: str
    body: List[Union["OWLFunc", rdflib.Literal, List[Union["OWLFunc", rdflib.Literal]]]]

    def __str__(self):
        body_str = ', '.join([str(b) for b in self.body])
        return f"{self.function}({body_str})"

    def _eval_body(self, arg: Union["OWLFunc", rdflib.Literal, str, List[Union["OWLFunc", rdflib.Literal, str]]]) -> \
            Union[str, FunOwlBase, List[FunOwlBase]]:
        if isinstance(arg, str):
            return arg
        if isinstance(arg, OWLFunc):
            return arg.eval()
        elif isinstance(arg, rdflib.Literal):
            if arg.datatype:
                return TypedLiteral(arg.value, arg.datatype)
            elif arg.language:
                return StringLiteralWithLanguage(arg.value, arg.language)
            else:
                return FunOwlChoice(StringLiteralNoLanguage(arg))
        else:
            return [self._eval_body(b) for b in arg]

    def eval(self) -> FunOwlBase:
        method_to_call = getattr(funowl, self.function, None)
        args = []
        annotations = []
        # Flatten nested lists and move annotations to the front
        for b in self.body:
            arg = self._eval_body(b)
            if isinstance(arg, Annotation):
                annotations.append(arg)
            else:
                args += arg if isinstance(arg, list) else [arg]

        if method_to_call is None:
            logging.getLogger().error(f"Unknown function: {self.str}")
            raise NotImplemented("Create an instance of FunOwlBase that reflects what is written to it ")
        # TODO: Address flattened arguments
        try:
            if annotations:
                return method_to_call(*args, annotations=annotations)
            else:
                return method_to_call(*args)
        except TypeError as e:
            arglist = ', '.join([str(arg) for arg in args])
            logging.error(f"function {method_to_call.__name__}({arglist})")
            raise e


def m_rem(m: Match) -> str:
    """ Return everything that doesn't match """
    return m.string[m.span()[1]:].strip()


def lit_parser(value: str, rest: str) -> Tuple[rdflib.Literal, str]:
    if rest.startswith('@'):
        m = literal_lang.match(rest)
        return rdflib.Literal(value, lang=m.group(1)), m_rem(m)
    elif rest.startswith('^^'):
        m = literal_datatype.match(rest)
        return rdflib.Literal(value, datatype=rdflib.URIRef(m.group(1))), m_rem(m)
    else:
        return rdflib.Literal(value), rest


def nested(s: str, depth=1) -> Tuple[str, str]:
    """
    Split string into everything inside a set of parens (leading has been removed) and everything outside
    :param s: string to split
    :param depth: starting depth
    :return: everything inside / everything outside
    """
    for i in range(0, len(s)):
        c = s[i]
        if c == '(':
            depth +=  1
        elif c == ')':
            depth -= 1
            if depth <= 0:
                return s[0:i], s[i+1:]
    raise ValueError("Parenthesis mismatch")


ARG_TYPE = Union[OWLFunc, rdflib.Literal, rdflib.URIRef]


def parse_args(s: str) -> List[Union[ARG_TYPE, List[ARG_TYPE]]]:
    """
     Parse an argument list to a function
    :param s: everything left inside the function
    :return: arguments split up into functions, urls, literals or lists thereof
    """
    rval = []
    unparsed = s
    while unparsed:
        unparsed =unparsed.strip()                          # Remove all white space
        m = comments_re.match(unparsed)
        if m:
            unparsed = unparsed[len(m.group(0)):]
            continue
        m = prefix_re.match(unparsed)
        if m:
            rval.append(m.group(1))
            rval.append(parse_args(m.group(2)))
            break
        m = function_re.match(unparsed)
        if m:
            body, unparsed = nested(m_rem(m))
            rval.append(OWLFunc(m.group(1), parse_args(body)))
            continue
        m = abs_uri.match(unparsed)
        if m:
            rval.append(rdflib.URIRef(m.group(1)))
            unparsed = m_rem(m)
            continue
        m = rel_uri.match(unparsed)
        if m:
            rval.append(rdflib.URIRef(m.group(1)))
            unparsed = m_rem(m)
            continue
        m = nested_re.match(unparsed)
        if m:
            body, unparsed = nested(m.group(1).strip())
            rval.append(parse_args(body))
            continue
        m = literal_re.match(unparsed)
        if m:
            lit, unparsed = lit_parser(m.group(1), m_rem(m))
            rval.append(lit)
            continue
        raise ValueError(f"Unrecognized content: {unparsed[:20]}")
    return rval


def fparse(s: str) -> List[OWLFunc]:
    """
     Parse functional syntax string and list of OWL Functions
    :param s: OWL string to parse
    :return: list of OWLFunc entries
    """
    rval: List[OWLFunc] = []
    unparsed = s
    while unparsed:
        unparsed = unparsed.strip()
        m = function_re.match(unparsed)
        if not m:
            raise ValueError("Unrecognized functional syntax string")
        body, unparsed = nested(m_rem(m))
        rval.append(OWLFunc(m.group(1), parse_args(body)))
    return rval


def to_python(defn: str) -> Optional[Ontology]:
    rval = None

    tree = fparse(defn)
    logging.debug(pformat(defn))

    if tree:
        prefixes: List[Prefix] = []

        for e in tree:
            decl = e.eval()
            if isinstance(decl, funowl.Prefix):
                prefixes.append(decl)
            else:
                rval = cast(funowl.Ontology, decl)
                prefix_reprs = {prefix.prefixName: prefix.fullIRI for prefix in prefixes}
                rval.prefixes(None, **prefix_reprs)
    return rval
