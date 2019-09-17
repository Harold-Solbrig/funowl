import os
from typing import Generator, Union, Tuple

from rdflib import Graph, Namespace, RDF, URIRef

from tests import datadir

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

    def rdf_to_functional(self, content: str) -> str:
        print(content)

    def next(self) -> Tuple[URIRef, str]:
        while(1):
            subj = next(self._iter)
            for syntax in self.g.objects(subj, TEST.normativeSyntax):
                if syntax == TEST.FUNCTIONAL:
                    return subj, self.g.value(subj, TEST.fsPremiseOntology, any=False)
                elif syntax == TEST.RDFXML:
                    return subj, self.rdf_to_functional(self.g.value(subj, TEST.rdfXmlPremiseOntology, any=False))


ncases = 0
for subj, txt in TestCases(os.path.join(datadir, 'all.rdf')):
    print(str(subj))
    ncases += 1


print(f"Number of test cases: {ncases}")
