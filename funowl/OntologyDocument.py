"""
ontologyDocument := { prefixDeclaration } Ontology
prefixDeclaration := 'Prefix' '(' prefixName '=' fullIRI ')'
directlyImportsDocuments := { 'Import' '(' IRI ')' }
Ontology :=
   'Ontology' '(' [ ontologyIRI [ versionIRI ] ]
      directlyImportsDocuments
      ontologyAnnotations
      axioms
   ')'
"""
from dataclasses import dataclass
from typing import Optional, List, Union, Dict

from rdflib import URIRef
from rdflib.extras.infixowl import Ontology

from funowl.Annotations import Annotation, AnnotationValue, AnnotationProperty, Annotatable
from funowl.Axioms import Axiom
from funowl.ClassAxioms import SubClassOf
from funowl.ClassExpressions import Class
from funowl.FunOwlBase import FunOwlBase, empty_list
from funowl.GeneralDefinitions import PrefixName, FullIRI
from funowl.Identifiers import IRI


@dataclass
class PrefixDeclaration(FunOwlBase):
    prefixName: Optional[PrefixName]
    fullIRI: FullIRI

    def as_owl(self, indent: int = 0) -> str:
        return self.i(indent) + 'Prefix' + '(' + self.owl_str(self.prefixName) + ':=' + self.owl_str(self.fullIRI) + ')'


@dataclass
class Import(FunOwlBase):
    iri: Union[Ontology, IRI]

    def as_owl(self, indent: int = 0) -> str:
        if isinstance(self.iri, Ontology) and self.iri.iri is None:
            raise ValueError(f"Imported ontology IRI is not specified")
        return self.func_name(indent,
                              lambda i1: (self.iri.iri if isinstance(self.iri, Ontology) else self.iri).as_owl())


@dataclass
class Ontology(Annotatable):
    iri: Optional[IRI] = None
    version: Optional[IRI] = None
    prefixDeclarations: List[PrefixDeclaration] = empty_list()
    directlyImportsDocuments: List[Import] = empty_list()
    axioms: List[Axiom] = empty_list()
    annotations: List[Annotation] = empty_list()

    def _add_or_replace_prefix(self, prefix: Optional[str], iri: str) -> None:
        for pd in self.prefixDeclarations:
            if pd.prefixName is None and prefix is None or str(pd.prefixName) == prefix:
                pd.fullIRI = iri
                return
        self.prefixDeclarations.append(PrefixDeclaration(PrefixName(prefix), FullIRI(str(iri))))

    def prefixes(self, base: Optional[FullIRI] = None,
                 **namedprefix: Dict[str, str]) -> "Ontology":
        if base is not None:
            self._add_or_replace_prefix(None, base)
        for pn, iri in namedprefix.items():
            self._add_or_replace_prefix(str(pn), str(iri))
        return self

    def annotation(self, prop: AnnotationProperty, value: AnnotationValue) -> "Ontology":
        self.annotations.append(Annotation(self._cast(AnnotationProperty, prop),
                                           self._cast(AnnotationValue, value)))
        return self

    def subClassOf(self, sub: Union[IRI, URIRef, str], sup: Union[IRI, URIRef, str]) -> "Ontology":
        self.axioms.append(SubClassOf(Class(sub), Class(sup)))
        return self

    def imports(self, import_: Union[Ontology, str]) -> "Ontology":
        self.directlyImportsDocuments.append(
            Import(import_.iri if isinstance(import_, Ontology) else IRI(str(import_))))
        return self

    def as_owl(self, indent: int = 0) -> str:
        if self.version and not self.iri:
            raise ValueError(f"Ontology cannot have a versionIRI ({self.version} without an ontologyIRI")
        return self.i(indent) + self.iter(indent, self.prefixDeclarations) + '\n' + \
            self.func_name(indent,
                           lambda i1: self.opt(self.iri, sep='') + self.opt(self.version) + '\n' +
                                      self.iter(i1+1, self.directlyImportsDocuments) +
                                      self.iter(i1+1, self.annotations) +
                                      self.iter(i1+1, self.axioms))
