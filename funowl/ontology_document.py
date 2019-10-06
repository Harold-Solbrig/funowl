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

from rdflib.extras.infixowl import Ontology

from funowl.annotations import Annotation, AnnotationValue, AnnotationProperty, Annotatable
from funowl.axioms import Axiom
from funowl.base.fun_owl_base import FunOwlBase
from funowl.base.list_support import empty_list
from funowl.class_axioms import SubClassOf
from funowl.class_expressions import Class, ClassExpression
from funowl.declarations import Declaration
from funowl.general_definitions import PrefixName, FullIRI
from funowl.identifiers import IRI
from funowl.objectproperty_axioms import SubObjectPropertyOf, SubObjectPropertyExpression, InverseObjectProperties, \
    FunctionalObjectProperty, InverseFunctionalObjectProperty, ObjectPropertyDomain, ObjectPropertyRange
from funowl.objectproperty_expressions import ObjectPropertyExpression
from funowl.prefix_declarations import PrefixDeclarations, Prefix
from funowl.writers.FunctionalWriter import FunctionalWriter


@dataclass
class Import(FunOwlBase):
    iri: Union[Ontology, IRI]

    def ontology_iri(self) -> IRI:
        return self.iri if isinstance(self.iri, IRI) else self.iri.iri

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.iri))


@dataclass
class Ontology(Annotatable):
    iri: Optional[IRI.types()] = None
    version: Optional[IRI.types()] = None
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

    def annotation(self, prop: AnnotationProperty.types(), value: AnnotationValue.types()) -> "Ontology":
        self.annotations.append(Annotation(prop, value))
        return self

    def declaration(self, decl: Declaration.types()) -> "Ontology":
        self.axioms.append(Declaration(decl))
        return self

    def subClassOf(self, sub: IRI.types(), sup: IRI.types()) -> "Ontology":
        subc = Class(sub)
        supc = Class(sup)
        # self.declaration(subc).declaration(supc)
        self.axioms.append(SubClassOf(subc, supc))
        return self

    def subObjectPropertyOf(self, sub: SubObjectPropertyExpression.types(), sup: ObjectPropertyExpression.types()) \
            -> "Ontology":
        subp = SubObjectPropertyExpression(sub)
        supp = ObjectPropertyExpression(sup)
        # self.declaration(subp).declaration(supp)
        self.axioms.append(SubObjectPropertyOf(subp, supp))
        return self

    def inverseObjectProperties(self, exp1: ObjectPropertyExpression.types(), exp2: ObjectPropertyExpression.types()) \
            -> "Ontology":
        exp1p = ObjectPropertyExpression(exp1)
        exp2p = ObjectPropertyExpression(exp2)
        self.axioms.append(InverseObjectProperties(exp1p, exp2p))
        return self

    def functionalObjectProperty(self, ope: ObjectPropertyExpression.types()) -> "Ontology":
        opep = ObjectPropertyExpression(ope)
        self.axioms.append(FunctionalObjectProperty(opep))
        return self

    def inverseFunctionalObjectProperty(self, ope: ObjectPropertyExpression.types()) -> "Ontology":
        opep = ObjectPropertyExpression(ope)
        self.axioms.append(InverseFunctionalObjectProperty(opep))
        return self

    def objectPropertyDomain(self, ope: ObjectPropertyExpression.types(), ce: ClassExpression) -> "Ontology":
        self.axioms.append(ObjectPropertyDomain(ope, ce))
        return self

    def objectPropertyRange(self, ope: ObjectPropertyExpression.types(), ce: ClassExpression) -> "Ontology":
        self.axioms.append(ObjectPropertyRange(ope, ce))
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
            func(self, lambda: w.opt(self.iri).opt(self.version).br(bool(self.directlyImportsDocuments)).
                 iter(self.directlyImportsDocuments, indent=False).iter(self.annotations, indent=False).
                 iter(self.axioms, indent=False), indent=False)
