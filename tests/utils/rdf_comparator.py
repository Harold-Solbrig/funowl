import re
from contextlib import redirect_stdout
from io import StringIO
from typing import Union, Optional, Dict, Tuple

from rdflib import Graph, RDFS, RDF, OWL, BNode
from rdflib.compare import to_isomorphic, IsomorphicGraph, graph_diff

# See notes in TestCaseIssues.md -- we ignore these
from rdflib.term import Node

triples_to_ignore = [
    (OWL.Thing, RDF.type, OWL.Class),
    (RDFS.Class, RDF.type, OWL.Class),
    (OWL.sameAs, RDF.type, OWL.AnnotationProperty),
    (RDF.type, RDF.type, OWL.AnnotationProperty)
]


def to_graph(inp: Union[Graph, str], fmt: Optional[str] = "turtle") -> Graph:
    """
    Convert inp into a graph
    :param inp: Graph, file name, url or text
    :param fmt: expected format of inp
    :return: Graph representing inp
    """
    if isinstance(inp, Graph):
        return inp
    g = Graph()
    if not inp.strip().startswith('{') and '\n' not in inp and '\r' not in inp:
        with open(inp) as f:
            inp = f.read()
    g.parse(data=inp, format=fmt)
    return g


def print_triples(g: Graph) -> None:
    """
    Print the contents of g into stdout
    :param g: graph to print
    """
    g_text = re.sub(r'@prefix.*\n', '', g.serialize(format="turtle").decode())
    print(g_text)


def fix_subject_bnodes(g1: Graph, g2: Graph) -> None:
    """
    Remove equivalent entries in G1 and G2 where both contain singleton subjects in the form of
    BNode URI Non-bnode

    :param g1:
    :param g2:
    """
    def subj_list(g: Graph) -> Dict[BNode, Tuple[Node, Node]]:
        rval = {}
        for s in g.subjects():
            if isinstance(s, BNode):
                rval[s] = list(g.predicate_objects(s))
        return rval

    s1_entries = subj_list(g1)
    s2_entries = subj_list(g2)
    for s1, v1 in s1_entries.items():
        for s2, v2 in s2_entries.items():
            if v1 == v2:
                for p1, o1 in v1:
                    g1.remove((s1, p1, o1))
                for p2, o2 in v2:
                    g2.remove((s2, p2, o2))


def compare_rdf(expected: Union[Graph, str], actual: Union[Graph, str], fmt: Optional[str] = "turtle") -> Optional[str]:
    """
    Compare expected to actual, returning a string if there is a difference
    :param expected: expected RDF. Can be Graph, file name, uri or text
    :param actual: actual RDF. Can be Graph, file name, uri or text
    :param fmt: RDF format
    :return: None if they match else summary of difference
    """
    def rem_metadata(g: Graph) -> IsomorphicGraph:
        # Remove list declarations from target
        for s in g.subjects(RDF.type, RDF.List):
            g.remove((s, RDF.type, RDF.List))
        g_iso = to_isomorphic(g)
        return g_iso

    expected_graph = to_graph(expected, fmt)
    expected_isomorphic = rem_metadata(expected_graph)
    actual_graph = to_graph(actual, fmt)
    actual_isomorphic = rem_metadata(actual_graph)

    # Graph compare takes a Looong time
    in_both, in_old, in_new = graph_diff(expected_isomorphic, actual_isomorphic)
    # if old_iso != new_iso:
    #     in_both, in_old, in_new = graph_diff(old_iso, new_iso)

    old_len = len(list(in_old))
    if old_len:
        for t in triples_to_ignore:
            if t in in_old:
                print(f"WARNING: {t} removed from expected graph")
                in_old.remove(t)
        old_len = len(in_old)
    new_len = len(list(in_new))
    if old_len and new_len:
        fix_subject_bnodes(in_old, in_new)
        old_len = len(in_old)
        new_len = len(in_new)
    if old_len or new_len:
        txt = StringIO()
        with redirect_stdout(txt):
            print("----- Missing Triples -----")
            if old_len:
                print_triples(in_old)
            print("----- Added Triples -----")
            if new_len:
                print_triples(in_new)
        return txt.getvalue()
    return None
