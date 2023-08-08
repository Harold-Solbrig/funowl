from dataclasses import dataclass
from typing import Optional, Union, Iterable, Dict

from rdflib import Graph, RDF, RDFS, XSD, OWL, Namespace
from rdflib.namespace import NamespaceManager
from rdflib.term import URIRef

from funowl.base.fun_owl_base import FunOwlBase
from funowl.general_definitions import PrefixName, FullIRI
from funowl.writers.FunctionalWriter import FunctionalWriter

PREFIX_NAME_TYPE = Optional[Union[PrefixName, str]]
FULL_IRI_TYPE = Union[FullIRI, Namespace, URIRef, str]


@dataclass
class Prefix(FunOwlBase):
    prefixName: PREFIX_NAME_TYPE        # Always recorded as PrefixName
    fullIRI: FULL_IRI_TYPE              # Always recorded as FullURI

    def __post_init__(self):
        if self.prefixName is not None and not isinstance(self.prefixName, PrefixName):
            self.prefixName = PrefixName(self.prefixName)
        if not isinstance(self.fullIRI, FullIRI):
            self.fullIRI = FullIRI(self.fullIRI)

    def __hash__(self):
        return hash(self.prefixName)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w.concat((self.prefixName or '') + ':', '=',
                                             URIRef(str(self.fullIRI)).n3(), sep=' '))


# Table 2. Declarations of the Standard Prefix Names
#     Prefix name	Prefix IRI
#     rdf:	<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#     rdfs:	<http://www.w3.org/2000/01/rdf-schema#>
#     xsd:	<http://www.w3.org/2001/XMLSchema#>
#     owl:	<http://www.w3.org/2002/07/owl#>
RDF_PREFIX = Prefix('rdf', str(RDF))
RDFS_PREFIX = Prefix('rdfs', str(RDFS))
XSD_PREFIX = Prefix('xsd', str(XSD))
OWL_PREFIX = Prefix('owl', str(OWL))
# DEFAULT_PREFIX = Prefix(None, str(OWL))

PREFIX_PRESETS = {RDF_PREFIX, RDFS_PREFIX, XSD_PREFIX, OWL_PREFIX}


class PrefixDeclarations(NamespaceManager):
    def __init__(self, g: Optional[Graph] = None) -> None:
        self._init = True
        self._prefixMap: Dict[str, Prefix] = dict()
        if g is None:
            g = Graph(bind_namespaces="core")
        super().__init__(g, bind_namespaces="core")
        for prefix in PREFIX_PRESETS:
            self.bind(prefix.prefixName, prefix.fullIRI)
        self._init = False

    def __contains__(self, item: Union[Prefix, str]) -> bool:
        return str(item) in self._prefixMap

    def __getitem__(self, item: Union[Prefix, str]) -> URIRef:
        entry = self._prefixMap.get(str(item))
        return URIRef(entry.fullIRI)

    def as_prefixes(self) -> Iterable[Prefix]:
        """ Return the contents of the manager as a list of Prefixes """
        return self._prefixMap.values()

    def __setattr__(self, key, value):
        if key.startswith('_') or self._init or key in self.__dict__:
            super().__setattr__(key, value)
        else:
            self.bind(key, value)

    def append(self, decl: Prefix) -> None:
        self.bind(decl.prefixName, decl.fullIRI)

    def as_uri(self, prefix: Union[Prefix, str], namespace: str) -> Optional[URIRef]:
        """
        Map prefix/namespace into a URI
        :param prefix:
        :param namespace:
        :return:
        """
        prefix = str(prefix) if prefix else ''      # Guard against None creeping in
        if prefix in self._prefixMap:
            return URIRef(self._prefixMap[prefix].fullIRI + namespace)
        return None

    def bind(self, prefix: PREFIX_NAME_TYPE, namespace: FULL_IRI_TYPE, _=True, __=True):
        """ Bind w/ defaults overriden """
        prefix = str(prefix) if prefix else ''
        self._prefixMap[prefix] = Prefix(prefix, str(namespace))
        super().bind(prefix, str(namespace), override=True, replace=True)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.iter(self.as_prefixes(), indent=False)
