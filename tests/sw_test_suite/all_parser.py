import os
from typing import Generator, Union, Tuple, Optional
from urllib.parse import urlsplit

from rdflib import Graph, Namespace, RDF, URIRef

from tests import datadir
from tests.sw_test_suite.syntax_converter import convert, OWLFormat

TEST = Namespace("http://www.w3.org/2007/OWL/testOntology#")
SW = Namespace("http://owl.semanticweb.org/id/")


class TestCases:

    def __init__(self, test_case_file_loc: str, test_case_format="xml") -> None:
        self.g = Graph()
        self.g.load(test_case_file_loc, format=test_case_format)

    def __iter__(self):
        self._iter = self.g.subjects(RDF.type, TEST.TestCase)
        return self

    def __next__(self):
        return self.next()

    def rdf_to_functional(self, content: str) -> Optional[str]:
        return convert(content, output_format=OWLFormat.func)

    def functional_to_rdf(self, content: str) -> Optional[str]:
        return convert(content, output_format=OWLFormat.rdfxml)

    def next(self) -> Tuple[URIRef, str, str]:
        """ Return the URI, the Functional Syntax and the RDF syntax"""
        while(1):
            subj = next(self._iter)
            for syntax in self.g.objects(subj, TEST.normativeSyntax):
                if syntax == TEST.FUNCTIONAL:
                    func_val = self.g.value(subj, TEST.fsPremiseOntology, any=False)
                    return subj, func_val, self.functional_to_rdf(func_val)
                elif syntax == TEST.RDFXML:
                    rdf_val = self.g.value(subj, TEST.rdfXmlPremiseOntology, any=False)
                    return subj, self.rdf_to_functional(rdf_val), rdf_val


outputdir = os.path.join(os.path.dirname(__file__), 'data')

def write_conversion(subj: str, txt: Optional[str], fmt: str) -> bool:
    fpath = urlsplit(subj).path
    fname = os.path.basename(fpath)
    fdir = os.path.join(outputdir, *os.path.dirname(fpath).split('/'), "func")
    os.makedirs(fdir, exist_ok=True)
    if txt:
        outfile = os.path.join(outputdir, fdir, fname + '.' + fmt)
        with open(outfile, 'w') as f:
            f.write(txt)
        print(f"{outfile} written")
        return True
    else:
        print(f"* {subj} to {fmt} conversion error")
        return False


ncases = 0
for subj, func_txt, rdf_txt in TestCases(os.path.join(datadir, 'all.rdf')):
    write_conversion(subj, func_txt, "func")
    write_conversion(subj, rdf_txt, "rdf")
    ncases += 1


print(f"Number of test cases: {ncases}")
