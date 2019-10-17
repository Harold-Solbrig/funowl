""" IRI := fullIRI | abbreviatedIRI """
import logging
from dataclasses import dataclass
from typing import Union, ClassVar, Optional, Type

from rdflib import URIRef, Namespace, Graph, RDF
from rdflib.term import Node

from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.writers.FunctionalWriter import FunctionalWriter
from funowl.general_definitions import FullIRI, AbbreviatedIRI


@dataclass
class IRI(FunOwlChoice):
    """ IRI := fullIRI | abbreviatedIRI """
    v: Union[AbbreviatedIRI, FullIRI, str]
    rdf_type: ClassVar[URIRef] = None
    input_type: ClassVar[Type] = str

    def full_uri(self, g: Graph) -> Optional[URIRef]:
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

    def to_rdf(self, g: Graph) -> Optional[Node]:
        if self.rdf_type is None:
            raise ValueError(f"IRI type not specified for class {type(self).__name__}")
        fulluri = self.full_uri(g)
        if g is None:
            raise ValueError(f"Unknown prefix: {self.v}")
        g.add((fulluri, RDF.type, self.rdf_type))
        return fulluri
