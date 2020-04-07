import logging
import re
from contextlib import closing
from io import BytesIO
from mmap import mmap, ACCESS_READ
from typing import Union, List, Tuple, Match, Optional, Callable, IO
from urllib.request import urlopen, urlretrieve

import rdflib

import funowl
from funowl import Annotation, OntologyDocument, Ontology
from funowl.base.fun_owl_base import FunOwlBase
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.dataproperty_expressions import DataPropertyExpression
from funowl.literals import TypedLiteral, StringLiteralWithLanguage, StringLiteralNoLanguage
# Ontology definition
from funowl.objectproperty_expressions import ObjectPropertyExpression

# 1: Function '('
function_re = re.compile(rb'\s*([A-Z][A-Za-z]+)\s*\(', flags=re.DOTALL)
inner_function_re = re.compile(r'\s*([A-Z][A-Za-z]+)\s*\(', flags=re.DOTALL)

# 1: Prefix ':=' 2: URI
prefix_re = re.compile(r'\s*(\S*):\s*=\s*(\S*)', flags=re.DOTALL)

# nodeId
blank_node_label_re = re.compile(r'\s*(_:\S*)', flags=re.DOTALL)

# '<' 1:uri '>
abs_uri = re.compile(r'\s*<([^>]+)>', flags=re.DOTALL)
abs_uri_b = re.compile(rb'\s*<([^>]+)>', flags=re.DOTALL)

# 1: rel-url
rel_uri = re.compile(r'\s*((([A-Za-z_])[^(]*?)?:\S+)\s*', flags=re.DOTALL)
rel_uri_b = re.compile(rb'\s*((([A-Za-z_])[^(]*?)?:\S+)\s*', flags=re.DOTALL)

# 1: literal
literal_re = re.compile(r'\s*("(?:\\.|[^"\\])*"|\S+)\s*', flags=re.DOTALL)

# 1: lang
literal_lang = re.compile(r'@(\S+)')

# 1: datatype
literal_datatype = re.compile(r'\^\^(\S+)')

# '(' 1:
nested_re = re.compile(r'\(\s*(.+\s*\))', flags=re.DOTALL)

# Trailing paren for ontology
final_pren = re.compile(rb'\s*\)\s*$', flags=re.DOTALL)


# TODO: Where is this defined and how do we deal with different EOL's?
comments_re = re.compile(r'\s*#[^\n]*\n?', flags=re.DOTALL)
comments_re_b = re.compile(rb'\s*#[^\n]*\n?', flags=re.DOTALL)


ARG_TYPE = Union["OWLFunc", rdflib.Literal, rdflib.URIRef, str]


class OWLFunc:
    def __init__(self, function: str, body: List[Union[ARG_TYPE, List[ARG_TYPE]]]) -> None:
        self.decl = self.eval(function, body)

    def __str__(self):
        return str(self.decl)

    def __repr__(self):
        return repr(self.decl)

    @staticmethod
    def _eval_body(arg: Union[ARG_TYPE, List[ARG_TYPE]]) -> \
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

    def eval(self, function: str, body: List[Union[ARG_TYPE, List[ARG_TYPE]]]) -> FunOwlBase:
        """ Evaluate function against argument string """

        # Everything else gets processed normally
        method_to_call = getattr(funowl, function, None)
        args = []
        annotations = []

        # Flatten nested lists and move annotations to the front
        for b in body:
            arg = self._eval_body(b)
            if isinstance(arg, Annotation):
                annotations.append(arg)
            else:
                args += arg if isinstance(arg, list) else [arg]

        if method_to_call is None:
            logging.getLogger().error(f"Unknown function: {function}")
            raise NotImplemented(f"Method {function} is not implemented")

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
    return m.string[m.span()[1]:]


def lit_parser(value: str, rest: str) -> Tuple[rdflib.Literal, str]:
    if len(value) > 1 and value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    if rest.startswith('@'):
        m = literal_lang.match(rest)
        return rdflib.Literal(value, lang=m.group(1)), m_rem(m)
    elif rest.startswith('^^'):
        m = literal_datatype.match(rest)
        return TypedLiteral(value, m.group(1)), m_rem(m)
    else:
        return rdflib.Literal(value), rest


def nested(s: bytes, start: int) -> Tuple[bytes, int]:
    """
    Return everything between start and a matching closing parenthesis
    :param s:
    :param start:
    :return:
    """
    depth = 1           # Because the function match eats the opening parenthesis
    i = start
    try:
        while True:
            m = s[i:i+1]
            if m == b'(':
                depth += 1
            elif m == b')':
                depth -= 1
                if depth <= 0:
                    return s[start:i], i+1
            i += 1
    except IndexError:
        raise ValueError("Parenthesis mismatch")


def uri_matcher(unparsed: Union[str, bytes], start: int) -> Tuple[Optional[rdflib.URIRef], int]:
    if isinstance(unparsed, (bytes, mmap)):
        m = abs_uri_b.match(unparsed, start)
        if m:
            return rdflib.URIRef(m.group(1).decode()), m.span()[1]
        m = rel_uri_b.match(unparsed, start)
        if m:
            return rdflib.URIRef(m.group(1).decode()), m.span()[1]
        return None, start
    else:
        m = abs_uri.match(unparsed, start)
        if m:
            return rdflib.URIRef(m.group(1)), m.span()[1]
        m = rel_uri.match(unparsed, start)
        if m:
            return m.group(1), m.span()[1]
        return None, start


def parse_args(s: str) -> List[Union[ARG_TYPE, List[ARG_TYPE]]]:
    """
    Parse an argument list to a function

    :param s: everything between the parenthesis
    :return: arguments split up into functions, urls, literals or lists thereof
    """
    rval = []
    unparsed = s
    while unparsed:
        unparsed = unparsed[skip_comments(unparsed, 0):]
        m = prefix_re.match(unparsed)
        if m:
            rval.append(m.group(1))
            rval.extend(parse_args(m.group(2)))
            unparsed = unparsed[m.span()[1]:]
            continue
        m = inner_function_re.match(unparsed)
        if m:
            body = bytes(m_rem(m), encoding='utf8')
            args, pos = nested(body, 0)
            unparsed = body[pos:].decode()
            rval.append(OWLFunc(m.group(1), parse_args(args.decode())))
            continue
        m = blank_node_label_re.match(unparsed)
        if m:
            rval.append(m.group(1))
            unparsed = unparsed[m.span()[1]:]
            continue
        uri, pos = uri_matcher(unparsed, 0)
        if uri:
            rval.append(uri)
            unparsed = unparsed[pos:]
            continue
        # The nasty little HasKey parenthesis bit
        unparsed = unparsed.strip()
        m = nested_re.match(unparsed)
        if m:
            body = bytes(m.group(1).strip(), encoding='utf8')
            args, pos = nested(body, 0)
            opes = parse_args(args.decode())
            unparsed = body[pos:].decode().strip()
            rval.extend([ObjectPropertyExpression(e) for e in opes])
            m = nested_re.match(unparsed)
            if not m:
                raise ValueError(f"HasKey DataPropertyExpressions clause missing: {unparsed}")
            body = bytes(m.group(1).strip(), encoding='utf8')
            args, pos = nested(body, 0)
            opes = parse_args(args.decode())
            unparsed = body[pos:].decode().strip()
            rval.extend([DataPropertyExpression(e) for e in opes])
            continue
        m = literal_re.match(unparsed)
        if m:
            lit, unparsed = lit_parser(m.group(1), m_rem(m))
            rval.append(lit)
            continue
        if unparsed:
            raise ValueError(f"Unrecognized content: {unparsed[:20]}")

    return rval


def skip_comments(inp: Union[bytes, str], start: int) -> int:
    if isinstance(inp, (bytes, mmap)):
        m = comments_re_b.match(inp, start)
        while m:
            start = m.span()[1]
            m = comments_re_b.match(inp, start)
    else:
        m = comments_re.match(inp, start)
        while m:
            start = m.span()[1]
            m = comments_re.match(inp, start)
    return start

def fparse(inp: bytes, start: int, consumer: Callable[[FunOwlBase], None]) -> int:
    """
    Functional parser - work through inp pulling complete functions out and processing them.
    :param inp: input byte stream
    :param start: current 0 based position in the stream
    :param consumer: OWLFunc entry consumer
    :return: final position
    """
    try:
        while True:
            start = skip_comments(inp, start)
            m = function_re.match(inp, start)
            if not m:
                break
            func = m.group(1).decode()
            start = m.span()[1]

            # Don't try to pre-parse the arguments for an Ontology
            if func == "Ontology":
                o = Ontology()
                start = skip_comments(inp, start)
                uri, start = uri_matcher(inp, start)
                if uri:
                    o.iri = uri
                    start = skip_comments(inp, start)
                    vers, start = uri_matcher(inp, start)
                    if vers:
                        o.version = vers
                start = skip_comments(inp, start)
                start = fparse(inp, start, lambda f: o.add_arg(f))
                consumer(o)
                start = skip_comments(inp, start)
                m = final_pren.match(inp, start)
                if not m:
                    raise ValueError("Missing final parenthesis")
                break
            else:
                body, start = nested(inp, start)
                consumer(OWLFunc(m.group(1).decode(), parse_args(body.decode())).decl)
    except IndexError:
        pass
    return start


def to_bytes_array(defn: Union[str, bytes, IO]) -> Union[bytes, mmap]:
    """ Find the target OWL resource and convert it to a bytes array.  "Why bytes?", you ask.  Some of the ontological
    resources that we have been called on to load (e.g. SNOMED CT) exceed 100MB in size.  Our parser is designed to
    consume resource information sequentially, so we have attempted to improve performance by using the mmap package.
    This, however, forces us to parse bytes vs. string arrays.
    :param defn: A file name, URL, open file handle, mmap, or simple string representing an owl ontology

    """
    if isinstance(defn, (bytes, mmap)):
        return defn
    elif hasattr(defn, 'read'):
        return mmap(defn.fileno(), 0, access=ACCESS_READ)
    elif '\n' in defn:
        return bytes(defn, encoding='utf8')
    elif '://' in defn:
        fname, resp = urlretrieve(defn)
        with closing(open(fname, 'r+b')) as f:
            return mmap(f.fileno(), 0, access=ACCESS_READ)
    else:
        with closing(open(defn, 'r+b')) as f:
            return mmap(f.fileno(), 0, access=ACCESS_READ)


def to_python(defn: Union[str, bytes, IO]) -> Optional[OntologyDocument]:
    """
    Convert the functional syntax in defn to a Python representation
    :param defn: The ontology definition
    :return: Ontology Document
    """
    def consumer(e: FunOwlBase) -> None:
        if isinstance(e, funowl.Prefix):
            ontology_doc.prefixDeclarations.append(e)
        elif isinstance(e, funowl.Ontology):
            ontology_doc.ontology = e
        else:
            logging.error("Unrecognized declaration")

    ontology_doc = OntologyDocument()
    fparse(to_bytes_array(defn), 0, consumer)
    return ontology_doc
