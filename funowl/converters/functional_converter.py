import re
from dataclasses import dataclass
from typing import Union, List, Tuple, Match

import rdflib

prefix_re = re.compile(r'\s*Prefix\s*\(\s*([^)]*)\s*\)', flags=re.DOTALL)
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
#   FunctIon ( args )
#   args = FunctIon | literal | embedded list
#   literal = URIRef | Literal
#   embedded list FunctIon|embedded list "(" args ")"

# 1: Function '('
function_re = re.compile(r'\s*([A-Z][A-Za-z]+)\s*\(', flags=re.DOTALL)
# 1: Prefix ':=' 2: URI
prefix_re = re.compile(r'(\S*):=\s*(\S*)', flags=re.DOTALL)
# '<' 1:uri '>
abs_uri = re.compile(r'<([^>]+)>', flags=re.DOTALL)
# 1: rel-url
rel_uri = re.compile(r'([A-Za-z_]?:\S+)', flags=re.DOTALL)
# 1: literal
literal_re = re.compile(r'("[^"]*"|\S+)', flags=re.DOTALL)
# 1: lang
literal_lang = re.compile(r'@(\S+)')
# 1: datatype
literal_datatype = re.compile(r'\^\^(\S+)')
# '(' 1:
nested_re = re.compile(r'\(\s*(.+\s*\))', flags=re.DOTALL)



@dataclass
class OWLFunc:
    """
    A function consists of a function name and a list consisting of owl functions, rdflib literals or lists of both """
    function: str
    body: List[Union["OWLFunc", rdflib.Literal, List[Union["OWLFunc", rdflib.Literal]]]]

    def __str__(self):
        body_str = ', '.join([str(b) for b in self.body])
        return f"{self.function}({body_str})"


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
        m = literal_re.match(unparsed)
        if m:
            lit, unparsed = lit_parser(m.group(1), m_rem(m))
            rval.append(lit)
            continue
        m = nested_re.match(unparsed)
        if m:
            body, unparsed = nested(m.group(1).strip())
            rval.append(parse_args(body))
            continue
        raise ValueError(f"Unrecognized content: {unparsed[:20]}")
    return rval


def fparse(s: str) -> List[OWLFunc]:
    rval: List[OWLFunc] = []
    unparsed = s
    while unparsed:
        m = function_re.match(unparsed.strip())
        if not m:
            raise ValueError("Unrecognized functional syntax string")
        body, unparsed = nested(m_rem(m))
        rval.append(OWLFunc(m.group(1), parse_args(body)))
    return rval


tree = fparse(func)
print('\n'.join([repr(e) for e in tree]))