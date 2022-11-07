from dataclasses import dataclass
from typing import Optional, List, Union, Iterable, Dict, OrderedDict

import rdflib.namespace
from rdflib import Graph, RDF, RDFS, XSD, OWL
from rdflib.term import URIRef

from funowl.base.fun_owl_base import FunOwlBase
from funowl.general_definitions import PrefixName, FullIRI
from funowl.writers.FunctionalWriter import FunctionalWriter


@dataclass
class Prefix(FunOwlBase):
    prefixName: Optional[Union[PrefixName, str]]    # Always recorded as PrefixName
    fullIRI: Union[FullIRI, str]                    # Always recorded as FullURI

    def __post_init__(self):
        if self.prefixName is not None and not isinstance(self.prefixName, PrefixName):
            self.prefixName = PrefixName(self.prefixName)
        if not isinstance(self.fullIRI, FullIRI):
            self.fullIRI = FullIRI(self.fullIRI)

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
DEFAULT_PREFIX = Prefix(None, str(OWL))


def prefix_presets() -> List[Prefix]:
    """
    The set of prefixes that are assumed without having to declare them. This function can be overridden if
    special handling is needed
    """
    return [RDF_PREFIX, RDFS_PREFIX, XSD_PREFIX, OWL_PREFIX, DEFAULT_PREFIX]


class PrefixDeclarations(OrderedDict):
    def __init__(self, g: Optional[Graph] = None, **kwargs) -> None:
        """
         Initialize a set of prefix declarations.  If g is supplied, export the prefixes in the graph.
        :param g: Graph containing a set of prefix declarations
        """
        super().__init__(**kwargs)


    def as_prefixes(self) -> Iterable[Prefix]:
        """ Return the contents of the manager as a list of Prefixes """
        return self._prefixMap.values()

    def __setattr__(self, key, value):
        key = '' if key is None else key
        if key.startswith('_') or key in self.__dict__:
            super().__setattr__(key, value)
        else:
            self._prefixMap[key] = Prefix(key, value)

    def __getattr__(self, item):
        item = str(item)
        if item.startswith('_') or item in self.__dict__:
            super().__getattribute__(item)
        return self._prefixMap[item]


    def append(self, decl: Prefix) -> None:
        self.bind(decl.prefixName, decl.fullIRI)

    def bind(self, prefix: str, namespace, _=True, __replace=True):
        """ Bind with override and replace defaults changed """
        if prefix:
            self._prefixmap[str(prefix)] = str(namespace)
        else:
            self._default = str(namespace)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.iter(self.as_prefixes(), indent=False)

    def normalizeUri(self, rdfTerm: str) -> str:
        """
        Takes an RDF Term and 'normalizes' it into a QName (using the
        registered prefix) or (unlike compute_qname) the Notation 3
        form for URIs: <...URI...>
        """
        try:
            namespace, name = split_uri(rdfTerm)
            if namespace not in self.__strie:
                insert_strie(self.__strie, self.__trie, str(namespace))
            namespace = URIRef(str(namespace))
        except:
            if isinstance(rdfTerm, Variable):
                return "?%s" % rdfTerm
            else:
                return "<%s>" % rdfTerm
        prefix = self.store.prefix(namespace)
        if prefix is None and isinstance(rdfTerm, Variable):
            return "?%s" % rdfTerm
        elif prefix is None:
            return "<%s>" % rdfTerm
        else:
            qNameParts = self.compute_qname(rdfTerm)
            return ":".join([qNameParts[0], qNameParts[-1]])

    def compute_qname(self, uri: str, generate: bool = True) -> Tuple[str, URIRef, str]:

        prefix: Optional[str]
        if uri not in self.__cache:

            if not _is_valid_uri(uri):
                raise ValueError(
                    '"{}" does not look like a valid URI, cannot serialize this. Did you want to urlencode it?'.format(
                        uri
                    )
                )

            try:
                namespace, name = split_uri(uri)
            except ValueError as e:
                namespace = URIRef(uri)
                prefix = self.store.prefix(namespace)
                if not prefix:
                    raise e
            if namespace not in self.__strie:
                insert_strie(self.__strie, self.__trie, namespace)

            if self.__strie[namespace]:
                pl_namespace = get_longest_namespace(self.__strie[namespace], uri)
                if pl_namespace is not None:
                    namespace = pl_namespace
                    name = uri[len(namespace):]

            namespace = URIRef(namespace)
            prefix = self.store.prefix(namespace)  # warning multiple prefixes problem

            if prefix is None:
                if not generate:
                    raise KeyError(
                        "No known prefix for {} and generate=False".format(namespace)
                    )
                num = 1
                while 1:
                    prefix = "ns%s" % num
                    if not self.store.namespace(prefix):
                        break
                    num += 1
                self.bind(prefix, namespace)
            self.__cache[uri] = (prefix, namespace, name)
        return self.__cache[uri]
