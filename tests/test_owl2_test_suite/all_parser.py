import logging
import os
from contextlib import redirect_stdout
from io import StringIO
from typing import Tuple, Optional
from urllib.parse import urlsplit

from rdflib import Graph, Namespace, RDF, URIRef
from rdflib.exceptions import ParserError

from tests import datadir
from tests.test_owl2_test_suite.syntax_converter import convert, OWLFormat

TEST = Namespace("http://www.w3.org/2007/OWL/testOntology#")
SW = Namespace("http://owl.semanticweb.org/id/")

CWD = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(CWD, '..', '..'))

# If you need to (re-) load specific files, put their names here.  If this array is empty, ALL test cases will be
# generated
files_to_process = [
    # "TestCase-3AWebOnt-2Dimports-2D014"
]


class TestCases:

    def __init__(self, test_case_file_loc: str, test_case_format="xml") -> None:
        self.g = Graph()
        self.g.load(test_case_file_loc, format=test_case_format)

    def __iter__(self):
        self._iter = self.g.subjects(RDF.type, TEST.TestCase)
        return self

    def __next__(self):
        return self.next()

    @staticmethod
    def xml_to_functional(key: str, content: str) -> Optional[str]:
        """ Convert RDF XML syntax to OWL functional """
        return convert(key, content, output_format=OWLFormat.func)

    @staticmethod
    def functional_to_xml(key: str, content: str) -> Optional[str]:
        """ Convert OWL functional syntax to RDF XML """
        return convert(key, content, output_format=OWLFormat.rdfxml)

    def next(self) -> Tuple[URIRef, str, Optional[Tuple[str, str, str]]]:
        """
        Return the subject URI, the native syntax and a tuple of the functional, rdf and original syntax
        The tuple is None if we can't get the original text
        """
        while True:
            subj = next(self._iter)
            if files_to_process:
                fname = os.path.basename(subj)
                if fname not in files_to_process:
                    continue
            for syntax in self.g.objects(subj, TEST.normativeSyntax):
                if syntax == TEST.FUNCTIONAL:
                    func_val = self.g.value(subj, TEST.fsPremiseOntology, any=False)
                    return subj, syntax, (func_val, self.functional_to_xml(subj, func_val), func_val)
                elif syntax == TEST.RDFXML:
                    orig_xml = self.g.value(subj, TEST.rdfXmlPremiseOntology, any=False)
                    if orig_xml is None:
                        orig_xml = self.g.value(subj, TEST.rdfXmlInputOntology, any=False)
                    if orig_xml is None:
                        return subj, syntax, None
                    func_val = self.xml_to_functional(subj, orig_xml)
                    xml_val = self.functional_to_xml(subj, func_val) if func_val else None
                    return subj, syntax, (func_val, xml_val, orig_xml)


nativedir = os.path.abspath(os.path.join(CWD, '..', 'data', 'all_test_files'))
outputdir = os.path.join(CWD, 'data')
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(filename=os.path.join(CWD, "all_parser.log"), filemode='w',
                    format='%(name)s %(levelname)s %(message)s')


def write_conversion(subj: str, txt: Optional[str], fmt: str, dir: str = outputdir) -> None:
    """
    Write txt to file indicated by subj using format fmt
    :param subj: subject of test
    :param txt: text to write
    :param fmt: format of text
    :param dir: target directory
    """
    fpath = urlsplit(subj).path.replace('-2D', '/').replace('-3A', '-').replace('/id/', '')
    fdir = os.path.join(dir, os.path.dirname(fpath))
    os.makedirs(fdir, exist_ok=True)
    if txt:
        outfile = os.path.join(dir, fdir, os.path.basename(fpath) + '.' + fmt)
        with open(outfile, 'w') as f:
            f.write(txt)
        logging.getLogger().info(f"{os.path.relpath(outfile, ROOT_DIR)} written")


ncases = 0
errors = dict()     # File name / error text

for subj, syntax, reprs in TestCases(os.path.join(datadir, 'all.rdf')):
    if reprs:
        func_txt, xml_txt, orig_txt = reprs
        write_conversion(subj, orig_txt, 'rdf' if syntax==TEST.RDFXML else 'func', nativedir)
        if func_txt:
            write_conversion(subj, func_txt, "func")
        else:
            errors[subj] = "XML to Functional Conversion Failure"
        if xml_txt:
            write_conversion(subj, xml_txt, "xml")
            g = Graph()
            try:
                g.parse(data=xml_txt)
                write_conversion(subj, g.serialize(format="turtle").decode(), 'ttl')
            except ParserError as e:
                errors[subj] = str(e)
        else:
            errors[subj] = "Functional to XML Conversion failure"
    else:
        errors[subj] = "Conversion failure"
    ncases += 1


logging.getLogger().info(f"Number of test cases: {ncases}")
logging.getLogger().info(f"Number of conversion errors: {len(errors)}")
for k, v in errors.items():
    logging.getLogger().error(f"\t{k}: {v}")
