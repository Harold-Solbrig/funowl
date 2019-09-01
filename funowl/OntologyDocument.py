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
from dataclasses import dataclass, field
from typing import Optional, List, Union, Dict

from rdflib import URIRef
from rdflib.extras.infixowl import Ontology

from funowl.Annotations import Annotation, AnnotationValue, AnnotationProperty, Annotatable
from funowl.Axioms import Axiom
from funowl.ClassAxioms import SubClassOf
from funowl.ClassExpressions import Class
from funowl.base.fun_owl_base import FunOwlBase
from funowl.base.list_support import empty_list
from funowl.writers.FunctionalWriter import FunctionalWriter
from funowl.GeneralDefinitions import PrefixName, FullIRI
from funowl.Identifiers import IRI
from funowl.PrefixDeclarations import PrefixDeclarations, Prefix


@dataclass
class Import(FunOwlBase):
    iri: Union[Ontology, IRI]

    def ontology_iri(self) -> IRI:
        return self.iri if isinstance(self.iri, IRI) else self.iri.iri

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.iri))


@dataclass
class Ontology(Annotatable):
    iri: Optional[IRI] = None
    version: Optional[IRI] = None
    prefixDeclarations: List[Prefix] = empty_list()
    directlyImportsDocuments: List[Import] = empty_list()
    axioms: List[Axiom] = empty_list()
    annotations: List[Annotation] = empty_list()

    # TODO: the relationship between prefixDeclarations and the manager is a wee bit brittle
    _prefixmanager: PrefixDeclarations = field(default=PrefixDeclarations(), init=False, repr=False)

    def __post_init__(self):
        for pd in self._prefixmanager.pdlist():
            if not self._has_prefix(pd.prefixName):
                self._prefixmanager.append(pd)

    def _has_prefix(self, pn: str) -> bool:
        for pd in self.prefixDeclarations:
            if pd.prefixName == pn or (not pn and not pd.prefixName):
                return True
        return False

    def __setattr__(self, key, value):
        if key == 'prefixDeclarations' and value:
            self.prefixDeclarations.append(Prefix(key, value))
        else:
            super().__setattr__(key, value)

    def __getattr__(self, item):
        rval = super().__getattribute__(item)
        return rval.pdlist() if item == 'prefixDeclarations' else rval

    def _add_or_replace_prefix(self, prefix: Optional[str], iri: str) -> None:
        for pd in self.prefixDeclarations:
            if pd.prefixName is None and prefix is None or str(pd.prefixName) == prefix:
                pd.fullIRI = iri
                self._prefixmanager.append(pd)
                return
        pd = Prefix(PrefixName(prefix) if prefix else None, FullIRI(str(iri)))
        self.prefixDeclarations.append(pd)
        self._prefixmanager.append(pd)

    def prefixes(self, base: Optional[FullIRI] = None,
                 **namedprefix: Dict[str, str]) -> "Ontology":
        if base is not None:
            self._add_or_replace_prefix(None, base)
        for pn, iri in namedprefix.items():
            self._add_or_replace_prefix(str(pn), str(iri))
        return self

    def annotation(self, prop: AnnotationProperty, value: AnnotationValue) -> "Ontology":
        self.annotations.append(Annotation(prop, value))
        return self

    def subClassOf(self, sub: Union[IRI, URIRef, str], sup: Union[IRI, URIRef, str]) -> "Ontology":
        self.axioms.append(SubClassOf(Class(sub), Class(sup)))
        return self

    def imports(self, import_: Union[Ontology, str]) -> "Ontology":
        self.directlyImportsDocuments.append(
            Import(import_.iri if isinstance(import_, Ontology) else IRI(str(import_))))
        return self

    def to_functional(self, w: Optional[FunctionalWriter] = None) -> FunctionalWriter:
        if self.version and not self.iri:
            raise ValueError(f"Ontology cannot have a versionIRI ({self.version} without an ontologyIRI")
        w = w or FunctionalWriter()
        return self._prefixmanager.to_functional(w).hardbr().\
            func(self, lambda: w.opt(self.iri).opt(self.version).iter(self.directlyImportsDocuments).iter(self.axioms))


