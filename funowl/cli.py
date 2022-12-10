import sys
from argparse import ArgumentParser
from typing import Optional, Union, List

from rdflib import Graph
from rdflib.plugin import plugins as rdflib_plugins
from rdflib.serializer import Serializer as rdflib_serializer
from rdflib.util import guess_format

from .converters.functional_converter import to_python

valid_formats = ["ttl"] + sorted(
        [x.name for x in rdflib_plugins(None, rdflib_serializer) if "/" not in str(x.name)]
    )
DEFAULT_FORMAT = "ttl"


def genargs(prog: Optional[str] = None) -> ArgumentParser:
    """
    Create a command line parser
    :return: parser
    """
    parser = ArgumentParser(prog, description="Convert OWL Functional Syntax to RDF")
    parser.add_argument("input", help="Input OWL functional syntax. Can be a file name or URL")
    parser.add_argument("output", help="Output file.  If omitted, output goes to stdout", nargs='?')
    parser.add_argument("-f", "--format", help="Output RDF Format.  If omitted, guess from output file suffix.\n"
                                               " If guessing doesn't work, assume 'turtle'",
                        choices=valid_formats)
    parser.add_argument("-np", "--noProgressBar", help="Don't output the progress indicators", action="store_true")
    return parser


def evaluate_cli(argv: Optional[Union[str, List[str]]] = None, prog: Optional[str] = None) -> int:
    if isinstance(argv, str):
        argv = argv.split()
    opts = genargs(prog).parse_args(argv if argv is not None else sys.argv[1:])

    # Read the functional syntax ontology
    ontology = to_python(opts.input, print_progress=bool(opts.output) and not opts.noProgressBar)

    # Convert to RDF
    g = Graph()
    ontology.to_rdf(g)

    # Emit as appropriate
    if opts.output:
        g.serialize(opts.output, format=opts.format or guess_format(opts.output) or DEFAULT_FORMAT)
    else:
        print(g.serialize(format=opts.format or DEFAULT_FORMAT))
    return 0


if __name__ == '__main__':
    evaluate_cli(sys.argv[1:])
