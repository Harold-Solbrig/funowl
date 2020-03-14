""" IRI := fullIRI | abbreviatedIRI """
import logging
from dataclasses import dataclass, Field
from typing import Union, ClassVar, Optional, Type

from rdflib import URIRef, Namespace, Graph, RDF, OWL, XSD, RDFS

from funowl.base.cast_function import exclude
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.general_definitions import FullIRI, AbbreviatedIRI
from funowl.writers.FunctionalWriter import FunctionalWriter

#TODO: determine whether this is needed
@dataclass(unsafe_hash=True)
class IRI(FunOwlChoice):
    """ IRI := fullIRI | abbreviatedIRI """
    v: Union[AbbreviatedIRI, FullIRI, URIRef, str] = exclude([URIRef, str])
    rdf_type: ClassVar[URIRef] = None
    _input_types: ClassVar[Type] = [URIRef, str]
    from_cast: bool = False

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
            # Filter: for (undocumented?) reasons, never assert owl:thing a owl:Class
            if not (fulluri.startswith(str(XSD)) or
                    fulluri.startswith(str(RDF)) or
                    fulluri.startswith(str(RDFS)) or
                    fulluri.startswith(str(OWL))
            ) or not self.from_cast:
                g.add((fulluri, RDF.type, self.rdf_type))

        return fulluri
