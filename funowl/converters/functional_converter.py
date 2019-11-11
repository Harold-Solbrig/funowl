import logging
import re
import sys
from pprint import pformat
from typing import Union, List, Tuple, Match, Optional, Callable

import rdflib

import funowl
from funowl import Prefix, Annotation, OntologyDocument, Ontology
from funowl.base.fun_owl_base import FunOwlBase
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.dataproperty_expressions import DataPropertyExpression
from funowl.literals import TypedLiteral, StringLiteralWithLanguage, StringLiteralNoLanguage
# Ontology definition
from funowl.objectproperty_expressions import ObjectPropertyExpression

ontology_re = re.compile(r'\s*Ontology\s*\((.*)\s*\)\s*$', flags=re.DOTALL)
# 1: Function '('
function_re = re.compile(r'([A-Z][A-Za-z]+)\s*\(', flags=re.DOTALL)
# 1: Prefix ':=' 2: URI
prefix_re = re.compile(r'(\S*):\s*=\s*(\S*)', flags=re.DOTALL)
# '<' 1:uri '>
abs_uri = re.compile(r'<([^>]+)>', flags=re.DOTALL)
# 1: rel-url
rel_uri = re.compile(r'((([A-Za-z_]).*?)?:\S+)', flags=re.DOTALL)
# 1: literal
literal_re = re.compile(r'("(?:\\.|[^"\\])*"|\S+)', flags=re.DOTALL)
# 1: lang
literal_lang = re.compile(r'@(\S+)')
# 1: datatype
literal_datatype = re.compile(r'\^\^(\S+)')
# '(' 1:
nested_re = re.compile(r'\(\s*(.+\s*\))', flags=re.DOTALL)

# TODO: Where is this defined and how do we deal with different EOL's?
comments_re = re.compile(r'#[^\n]*\n?', flags=re.DOTALL)


class OWLFunc:
    def __init__(self, function: str, body: str) -> None:
        self.decl = self.eval(function, body)

    def __str__(self):
        return str(self.decl)

    def __repr__(self):
        return repr(self.decl)

    @staticmethod
    def _eval_body(arg: Union["OWLFunc", rdflib.Literal, str, List[Union["OWLFunc", rdflib.Literal, str]]]) -> \
            Union[str, FunOwlBase, List[FunOwlBase]]:
        if isinstance(arg, str):
            return arg
        elif isinstance(arg, OWLFunc):
            return arg.decl
        elif isinstance(arg, rdflib.Literal):
            if arg.datatype:
                return TypedLiteral(arg.value, arg.datatype)
            elif arg.language:
                return StringLiteralWithLanguage(arg.value, arg.language)
            else:
                return FunOwlChoice(StringLiteralNoLanguage(arg))
        elif isinstance(arg, FunOwlBase):
            return arg
        else:
            return [OWLFunc._eval_body(b) for b in arg]

    def eval(self, function: str, arg_str: str) -> FunOwlBase:
        """ Evaluate function against argument string """

        # Ontology is processed differently because of the potential size of its contents -- we construct it one by
        # one unstead of trying to create a giant argument list
        if function == 'Ontology':
            ontology = Ontology()
            parse_args(arg_str, lambda e: ontology_processor(ontology, e))
            return ontology

        # Everything else gets processed normally
        method_to_call = getattr(funowl, function, None)
        args = []
        annotations = []
        body = []
        parse_args(arg_str, lambda e: body.append(e))

        # Flatten nested lists and move annotations to the front
        for b in body:
            arg = self._eval_body(b)
            if isinstance(arg, Annotation):
                annotations.append(arg)
            else:
                args += arg if isinstance(arg, list) else [arg]

        if method_to_call is None:
            logging.getLogger().error(f"Unknown function: {function}")
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


ARG_TYPE = Union[OWLFunc, rdflib.Literal, rdflib.URIRef, str]

num_entered = 0
def ontology_processor(ontology: Ontology, entry: Union[ARG_TYPE, List[ARG_TYPE]]) -> None:
    global num_entered
    ontology.add_arg(entry.decl if isinstance(entry, OWLFunc) else entry)
    num_entered += 1
    if not num_entered % 100:
        if not num_entered % 1000:
            if not num_entered % 10000:
                print("T", end='')
            else:
                print("K", end='')
        else:
            print('.', end='')
        sys.stdout.flush()


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


def parse_args(s: str, arg_processor: Callable[[Union[ARG_TYPE, List[ARG_TYPE]]], None] ) -> None:
    """
     Parse an argument list to a function
    :param s: everything left inside the function
    :param arg_processor: function to call with a new argument
    :return: arguments split up into functions, urls, literals or lists thereof
    """
    unparsed = s
    while unparsed:
        unparsed =unparsed.strip()                          # Remove all white space
        m = comments_re.match(unparsed)
        if m:
            unparsed = unparsed[len(m.group(0)):]
            continue
        m = prefix_re.match(unparsed)
        if m:
            arg_processor(m.group(1))
            parse_args(m.group(2), arg_processor)
            break
        m = function_re.match(unparsed)
        if m:
            body, unparsed = nested(m_rem(m))
            arg_processor(OWLFunc(m.group(1), body))
            continue
        m = abs_uri.match(unparsed)
        if m:
            arg_processor(rdflib.URIRef(m.group(1)))
            unparsed = m_rem(m)
            continue
        m = rel_uri.match(unparsed)
        if m:
            arg_processor(rdflib.URIRef(m.group(1)))
            unparsed = m_rem(m)
            continue
        m = nested_re.match(unparsed)
        if m:
            body, unparsed = nested(m.group(1).strip())
            parse_args(body, lambda e: arg_processor(ObjectPropertyExpression(e)))
            # arg_processor([ObjectPropertyExpression(e) for e in parse_args(body)])
            m = nested_re.match(unparsed.strip())
            if not m:
                raise ValueError(f"HasKey DataPropertyExpressions clause missing: {unparsed}")
            body, unparsed = nested(m.group(1).strip())
            parse_args(body, lambda e: arg_processor(DataPropertyExpression(e)))
            # arg_processor([DataPropertyExpression(e) for e in parse_args(body)])
            continue
        m = literal_re.match(unparsed)
        if m:
            lit, unparsed = lit_parser(m.group(1), m_rem(m))
            arg_processor(lit)
            continue
        raise ValueError(f"Unrecognized content: {unparsed[:20]}")


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
        rval.append(OWLFunc(m.group(1), body))

    return rval


def to_python(defn: str) -> Optional[OntologyDocument]:
    rval = None

    # An ontology document consists of any number of prefix declarations and exactly one (?) ontology declaration
    tree = fparse(defn)
    logging.debug(pformat(defn))

    if tree:
        prefixes: List[Prefix] = []

        for e in tree:
            if isinstance(e.decl, funowl.Prefix):
                prefixes.append(e.decl)
            elif isinstance(e.decl, funowl.Ontology):
                rval = OntologyDocument(*prefixes, ontology=e.decl)
            else:
                logging.error("Unrecognized declaration")
    return rval
