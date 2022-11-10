""" IRI := fullIRI | abbreviatedIRI """
import logging
from dataclasses import dataclass
from typing import Union, ClassVar, Optional, List

from rdflib import URIRef, Namespace, Graph, RDF, OWL, XSD, RDFS

from funowl.base.cast_function import exclude
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.base.rdftriple import SUBJ
from funowl.general_definitions import FullIRI, AbbreviatedIRI
from funowl.prefix_declarations import PrefixDeclarations
from funowl.writers.FunctionalWriter import FunctionalWriter


@dataclass(unsafe_hash=True)
class IRI(FunOwlChoice):
    """ IRI := fullIRI | abbreviatedIRI """
    v: Union[AbbreviatedIRI, FullIRI, URIRef, str] = exclude([URIRef, str])

    rdf_type: ClassVar[URIRef] = None
    prefix_declarations: ClassVar[PrefixDeclarations] = None        # Link to prefixes section, if declared

    # def __post_init__(self):
    #     print(f"Just constructed a {type(self)} value {str(self.v)}")

    def full_uri(self, g: Graph) -> Optional[URIRef]:
        if not isinstance(self.v, AbbreviatedIRI):
            return URIRef(self.v)
        prefix, lname = str(self).split(':', 1)
        if self.prefix_declarations and prefix in self.prefix_declarations:
            return self.prefix_declarations[prefix] + lname
        return self.v.to_rdf(g)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        """ Emit an abbreviated URI if possible, otherwise a full one """
        fulluri = None if isinstance(self.v, AbbreviatedIRI) else self.full_uri(w.g)
        return w + (fulluri.n3(w.g.namespace_manager) if fulluri else self.v)

    def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> URIRef:
        fulluri = self.full_uri(g)

        def is_builtin_namespace(n) -> bool:
            # Never add assertions that consist entirely of builtin types
            return (n.startswith(str(XSD)) or
                    n.startswith(str(RDF)) or
                    n.startswith(str(RDFS)) or
                    n.startswith(str(OWL)))

        if self.rdf_type:
            # Filter: for (undocumented?) reasons, never assert owl:thing a owl:Class
            if emit_type_arc or not is_builtin_namespace(fulluri) or not is_builtin_namespace(self.rdf_type):
                g.add((fulluri, RDF.type, self.rdf_type))
        return fulluri

    def _subjects(self, g: Graph) -> List[SUBJ]:
        return [self.full_uri(g)]
