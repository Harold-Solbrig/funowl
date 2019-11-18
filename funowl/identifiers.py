""" IRI := fullIRI | abbreviatedIRI """
import logging
from dataclasses import dataclass
from typing import Union, ClassVar, Optional, Type

from rdflib import URIRef, Namespace, Graph, RDF
from rdflib.term import Node

from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.writers.FunctionalWriter import FunctionalWriter
from funowl.general_definitions import FullIRI, AbbreviatedIRI


@dataclass(unsafe_hash=True)
class IRI(FunOwlChoice):
    """ IRI := fullIRI | abbreviatedIRI """
    v: Union[AbbreviatedIRI, FullIRI, URIRef, str]
    rdf_type: ClassVar[URIRef] = None
    input_type: ClassVar[Type] = str

    def full_uri(self, g: Graph) -> Optional[URIRef]:
        if isinstance(self.v, URIRef):
            return self.v
        if isinstance(self.v, AbbreviatedIRI):
            # TODO: find the code in rdflib that does this
            ns, local = self.v.split(':', 1)
            for ns1, uri in g.namespaces():
                if ns == ns1:
                    return(Namespace(uri)[local])
            logging.warning(f"IRI: {self.v} - {ns} not a valid prefix")
            return None
        if isinstance(self.v, FullIRI):
            return URIRef(self.v)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        fulluri = self.full_uri(w.g)
        return w + (fulluri.n3(w.g.namespace_manager) if fulluri else self.v)

    def to_rdf(self, g: Graph) -> URIRef:
        fulluri = self.full_uri(g)
        if self.rdf_type:
            g.add((fulluri, RDF.type, self.rdf_type))

        return fulluri
