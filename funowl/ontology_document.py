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
import sys
from dataclasses import dataclass, MISSING
from typing import Optional, List, Union, Dict, cast

from rdflib import Graph, RDF, OWL, URIRef, BNode

from funowl.annotations import Annotation, AnnotationValue, AnnotationProperty, Annotatable
from funowl.axioms import Axiom
from funowl.base.fun_owl_base import FunOwlBase
from funowl.base.list_support import empty_list
from funowl.base.rdftriple import NODE, SUBJ
from funowl.class_axioms import SubClassOf, EquivalentClasses
from funowl.class_expressions import Class, ClassExpression
from funowl.declarations import Declaration
from funowl.general_definitions import PrefixName, FullIRI
from funowl.identifiers import IRI
from funowl.individuals import NamedIndividual
from funowl.objectproperty_axioms import SubObjectPropertyOf, SubObjectPropertyExpression, InverseObjectProperties, \
    FunctionalObjectProperty, InverseFunctionalObjectProperty, ObjectPropertyDomain, ObjectPropertyRange
from funowl.objectproperty_expressions import ObjectPropertyExpression
from funowl.prefix_declarations import Prefix
from funowl.terminals.TypingHelper import isinstance_
from funowl.writers.FunctionalWriter import FunctionalWriter


@dataclass
class Import(FunOwlBase):
    iri: Union["Ontology", IRI]

    def ontology_iri(self) -> IRI:
        return self.iri if isinstance(self.iri, IRI) else self.iri.iri

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: (w + self.iri))

    def to_rdf(self, _: Graph) -> Optional[NODE]:
        return URIRef(str(self.ontology_iri()))


@dataclass
class Ontology(Annotatable):
    iri: Optional[IRI.types()] = None
    version: Optional[IRI.types()] = None
    directlyImportsDocuments: List[Import] = empty_list()
    axioms: List[Axiom] = empty_list()
    annotations: List[Annotation] = empty_list()

    def __init__(self, *args: Union[FunOwlBase, IRI.types()], **kwargs: Dict[str, FunOwlBase]) -> None:
        args = list(args)
        if args and isinstance(args[0], IRI) and not isinstance_(args[0], Axiom):
            self.iri = args.pop(0)
        if args and isinstance(args[0], IRI) and not isinstance_(args[0], Axiom):
            self.version = args.pop(0)
        self.directlyImportsDocuments = cast(List[Import], [])
        while args and isinstance(args[0], Import):
            self.directlyImportsDocuments.append(args.pop(0))
        self.axioms = cast(List[Axiom], [])
        while args and isinstance_(args[0], Axiom):
            self.axioms.append(args.pop(0))
        self.annotations = kwargs.get('annotations', [])
        for k, v in kwargs.items():
            cur_v = getattr(self, k, MISSING)
            if cur_v is MISSING:
                raise ValueError(f"Unknown argument to Ontology: {k}")
            if cur_v is None:
                setattr(self, k, v)
            elif k != 'annotations':
                setattr(self, k, cur_v + v)

        if args:
            raise ValueError(f"Unrecognized arguments to Ontology: {args}")
        self._naxioms = 0

    def add_arg(self, arg: [IRI.types(), Import, Axiom, Annotation]):
        if isinstance_(arg, Axiom):
            self.axioms.append(arg)
            self._naxioms += 1
            if not self._naxioms % 100000:
                print('H')
            elif not self._naxioms % 10000:
                print('K')
            elif not self._naxioms % 1000:
                print('k', end='')
                sys.stdout.flush()
            elif not self._naxioms % 100:
                print('.', end='')
                sys.stdout.flush()
        elif isinstance(arg, IRI):
            if not self.iri:
                self.iri = arg
            elif not self.version:
                self.version = arg
            else:
                raise ValueError(f"Raw IRI is not a valid argument {arg}")
        elif isinstance(arg, Import):
            self.directlyImportsDocuments.append(arg)
        elif isinstance(arg, Annotation):
            self.annotations.append(arg)
        else:
            raise ValueError(f"Unrecognized argument to Ontology: {arg}")


    # =======================
    # Syntactic sugar -- fill these in as needed
    # =======================
    def annotation(self, prop: AnnotationProperty.types(), value: AnnotationValue.types()) -> "Ontology":
        self.annotations.append(Annotation(prop, value))
        return self

    def declarations(self, *declarations: Declaration.types()) -> "Ontology":
        for declaration in declarations:
            self.axioms.append(Declaration(declaration))
        return self

    def subClassOf(self, sub: Class.types(), sup: Class.types()) -> "Ontology":
        if not issubclass(type(sub), Class) and isinstance(sub, Class):
            sub = Class(sub)
        if not issubclass(type(sup), Class) and isinstance(sup, Class):
            sup = Class(sup)
        self.axioms.append(SubClassOf(sub, sup))
        return self

    def equivalentClasses(self, *classExpressions: ClassExpression) -> "Ontology":
        self.axioms.append(EquivalentClasses(*classExpressions))
        return self

    def subObjectPropertyOf(self, sub: SubObjectPropertyExpression.types(), sup: ObjectPropertyExpression.types()) \
            -> "Ontology":
        subp = SubObjectPropertyExpression(sub)
        supp = ObjectPropertyExpression(sup)
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

    def imports(self, import_: Union["Ontology", str]) -> "Ontology":
        self.directlyImportsDocuments.append(
            Import(import_.iri if isinstance(import_, Ontology) else IRI(str(import_))))
        return self

    def namedIndividuals(self, *individuals: IRI.types()) -> "Ontology":
        for individual in individuals:
            self.axioms.append(NamedIndividual(individual))

    # ====================
    # Conversion functions
    # ====================

    def to_functional(self, w: Optional[FunctionalWriter]) -> FunctionalWriter:
        """ Return a FunctionalWriter instance with the representation of the ontology in functional syntax """
        if self.version and not self.iri:
            raise ValueError(f"Ontology cannot have a versionIRI ({self.version} without an ontologyIRI")
        w = w or FunctionalWriter()
        return w.func(self, lambda: w.opt(self.iri).opt(self.version).
                 br(bool(self.directlyImportsDocuments) or bool(self.annotations) or bool(self.axioms)).
                 iter(self.directlyImportsDocuments, indent=False).iter(self.annotations, indent=False).
                 iter(self.axioms, indent=False), indent=False)

    def to_rdf(self, g: Graph) -> SUBJ:
        ontology_uri = self.iri.to_rdf(g) if self.iri else BNode()
        version_uri = self.version.to_rdf(g) if self.version else None
        g.add((ontology_uri, RDF.type, OWL.Ontology))
        if self.version:
            g.add((ontology_uri, OWL.versionIRI, version_uri))
        for imp in self.directlyImportsDocuments:
            g.add((ontology_uri, OWL.imports, imp.to_rdf(g)))
        for axiom in self.axioms:
            axiom.to_rdf(g)
        super().to_rdf(g)
        return ontology_uri


@dataclass
class OntologyDocument(FunOwlBase):
    """
    prefixDeclarations are
    """
    prefixDeclarations: List[Prefix] = empty_list()
    ontology: Ontology = None

    def __init__(self, default_prefix: FullIRI = None, ontology: Optional[Ontology] = None, **prefixes: FullIRI):
        self.prefixDeclarations = []
        self.ontology = ontology if ontology is not None else Ontology()
        if default_prefix:
            self.prefixDeclarations.append(Prefix(None, default_prefix))
        if prefixes:
            for k, v in prefixes.items():
                self.prefixDeclarations.append(Prefix(k, v))

    def prefixes(self, dflt: Optional[FullIRI], **prefixes: FullIRI) -> None:
        if dflt:
            self.prefixDeclarations.append(Prefix('', dflt))
        for ns, iri in prefixes.items():
            self.prefixDeclarations.append(Prefix(PrefixName(ns), iri))

    def __setattr__(self, key: str, value) -> None:
        if key.startswith('_') or key in ('prefixDeclarations', 'ontology'):
            super().__setattr__(key, value)
        else:
            prefix = Prefix(PrefixName(key) if key else None, FullIRI(value))
            self.prefixDeclarations.append(prefix)

    def __getattr__(self, item):
        # This gets called only when something isn't already in the dictionary
        if isinstance(item, PrefixName):
            for p in self.prefixDeclarations:
                if p.prefixName == item:
                    return p.fullIRI
        return super().__getattribute__(item)

    def add_namespaces(self, g: Graph) -> Graph:
        for prefix in self.prefixDeclarations:
            g.namespace_manager.bind(str(prefix.prefixName or ''), str(prefix.fullIRI), True, True)
        return g

    def to_functional(self, w: Optional[FunctionalWriter] = None) -> FunctionalWriter:
        """ Return a FunctionalWriter instance with the representation of the OntologyDocument in functional syntax """
        w = w or FunctionalWriter()
        self.add_namespaces(w.g)
        return w.iter([Prefix(ns, uri) for ns, uri in w.g.namespaces()], indent=False).hardbr() +\
               (self.ontology or Ontology())

    def to_rdf(self, g: Graph) -> SUBJ:
        self.add_namespaces(g)
        return self.ontology.to_rdf(g)
