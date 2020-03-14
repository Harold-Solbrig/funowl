from typing import Dict
from rdflib import Graph, BNode
from rdflib.term import Node

# If TRUE, annotation axioms will make copies of BNodes rather than referencing them directly.  This allows us to pass
# the OWL2 conformance suite, but makes it difficult to determine what is getting annotated.  See: ../TestCaseIssues.md
# for further information
USE_BNODE_COPIES = True


def clone_subgraph(g: Graph, subj: Node, seen: Dict[Node, Node] = None) -> Node:
    """
     If subj is a BNode, make a copy of it, making copyies of any BNode objects
    :param g: Graph containing subj.  Copy of subj is added to this
    :param subj: Subject
    :param seen: recursion detection
    :return: Node identifier of (possible) copy
    """
    if not isinstance(subj, BNode):
        return subj
    if seen is None:
        seen = dict()
    elif subj in seen:
        return seen[subj]
    new_subj = BNode()
    seen[subj] = new_subj
    for p, o in g.predicate_objects(subj):
        g.add((new_subj, p, clone_subgraph(g, o, seen)))
    return new_subj
