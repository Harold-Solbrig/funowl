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

from rdflib import Graph, RDF, OWL, URIRef, BNode, Literal as Rdflib_Literal, Namespace

from funowl.annotations import Annotation, AnnotationValue, AnnotationProperty, Annotatable
from funowl.assertions import DataPropertyAssertion
from funowl.axioms import Axiom
from funowl.base.fun_owl_base import FunOwlBase
from funowl.base.list_support import empty_list_wrapper
from funowl.base.rdftriple import NODE, SUBJ
from funowl.class_axioms import SubClassOf, EquivalentClasses
from funowl.class_expressions import Class, ClassExpression
from funowl.dataproperty_expressions import DataPropertyExpression
from funowl.declarations import Declaration
from funowl.general_definitions import PrefixName, FullIRI
from funowl.identifiers import IRI
from funowl.individuals import NamedIndividual, Individual
from funowl.literals import Literal
from funowl.objectproperty_axioms import SubObjectPropertyOf, SubObjectPropertyExpression, InverseObjectProperties, \
    FunctionalObjectProperty, InverseFunctionalObjectProperty, ObjectPropertyDomain, ObjectPropertyRange
from funowl.objectproperty_expressions import ObjectPropertyExpression
from funowl.prefix_declarations import Prefix
from funowl.terminals.TypingHelper import isinstance_, proc_forwards
from funowl.writers.FunctionalWriter import FunctionalWriter

# Predicate that references the literal representation of the functional syntax of a subject
# TODO: Add code that includes the complete definition of this predicate
FUNOWL_URI = Namespace("http://ontologies-r.us/funowl/")
FUNOWL_NAMESPACE = "funowl"
IN_FUNCTIONAL = FUNOWL_URI.functional_definition

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
    # annotation_type = OWL.Ontology
    iri: Optional[IRI] = None
    version: Optional[IRI] = None
    directlyImportsDocuments: List[Import] = empty_list_wrapper(Import)
    axioms: List[Axiom] = empty_list_wrapper(Axiom)
    annotations: List[Annotation] = empty_list_wrapper(Annotation)

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
                print(self._naxioms)
            elif not self._naxioms % 10000:
                print(self._naxioms)
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
        return self

    def dataPropertyAssertion(self, expr: DataPropertyExpression.types(), sourceIndividual: Individual.types(),
                              targetValue: Literal.types()) -> "Ontology":
        self.axioms.append(DataPropertyAssertion(expr, sourceIndividual, targetValue))
        return self

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

    def _add_functional_definition(self, g: Graph, s: SUBJ, n: FunOwlBase) -> None:
        """ Add a functional definition for n to g """
        functional_definition = n.to_functional(FunctionalWriter(g=g, tab=' '))
        g.add( (s, IN_FUNCTIONAL, Rdflib_Literal(functional_definition.getvalue())) )

    def to_rdf(self, g: Graph, emit_type_arc: bool = False, emit_functional_definitions: bool = False) -> SUBJ:
        """
        Emit the ontology document in RDF syntax into graph g
        :param g: target graph
        :param emit_type_arc:
        :param emit_functional_definitions: True means add functional definitions of each subject
        :return:
        """
        ontology_uri = self.iri.to_rdf(g) if self.iri else BNode()
        version_uri = self.version.to_rdf(g) if self.version else None
        g.add((ontology_uri, RDF.type, OWL.Ontology))
        for annotation in self.annotations:
            t = (ontology_uri, annotation.property.to_rdf(g), annotation.value.to_rdf(g))
            g.add(t)
            annotation.TANN(g, t)
            if emit_functional_definitions:
                self._add_functional_definition(g, ontology_uri, annotation)
        if self.version:
            g.add((ontology_uri, OWL.versionIRI, version_uri))
        for imp in self.directlyImportsDocuments:
            g.add((ontology_uri, OWL.imports, imp.to_rdf(g)))
            if emit_functional_definitions:
                self._add_functional_definition(g, ontology_uri, imp)
        for axiom in self.axioms:
            axiom.to_rdf(g)
            if emit_functional_definitions:
                subjs = axiom._subjects(g)
                for subj in subjs:
                    self._add_functional_definition(g, subj, axiom)
        return ontology_uri


@dataclass
class OntologyDocument(FunOwlBase):
    """
    prefixDeclarations are
    """
    prefixDeclarations: List[Prefix] = empty_list_wrapper(Prefix)
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

    def __str__(self) -> str:
        return self.to_functional().getvalue()

    def add_namespaces(self, g: Graph, add_funowl_namespace: bool = False) -> Graph:
        for prefix in self.prefixDeclarations:
            g.namespace_manager.bind(str(prefix.prefixName or ''), str(prefix.fullIRI), True, True)
        if add_funowl_namespace:
            g.namespace_manager.bind(FUNOWL_NAMESPACE, FUNOWL_URI)
        return g

    def to_functional(self, w: Optional[FunctionalWriter] = None) -> FunctionalWriter:
        """ Return a FunctionalWriter instance with the representation of the OntologyDocument in functional syntax """
        w = w or FunctionalWriter()
        self.add_namespaces(w.g)
        return w.iter([Prefix(ns, uri) for ns, uri in w.g.namespaces()], indent=False).hardbr() + \
               (self.ontology or Ontology())

    def to_rdf(self, g: Graph, emit_type_arc: bool = False, emit_functional_definitions: bool = False) -> SUBJ:
        """ Convert the ontology document into RDF representation """
        self.add_namespaces(g, add_funowl_namespace=emit_functional_definitions)
        return self.ontology.to_rdf(g, emit_type_arc, emit_functional_definitions)


proc_forwards(Import, globals())
