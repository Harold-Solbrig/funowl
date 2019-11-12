#%%

# Pizza Ontology Sample

#%% md

"""xml
<rdf:RDF xmlns="http://www.co-ode.org/ontologies/pizza/pizza.owl#"
     xml:base="http://www.co-ode.org/ontologies/pizza/pizza.owl"
     xmlns:pizza="http://www.co-ode.org/ontologies/pizza/pizza.owl#"
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     xmlns:terms="http://purl.org/dc/terms/"
     xmlns:owl="http://www.w3.org/2002/07/owl#"
     xmlns:xml="http://www.w3.org/XML/1998/namespace"
     xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
     xmlns:skos="http://www.w3.org/2004/02/skos/core#"
     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
     xmlns:dc="http://purl.org/dc/elements/1.1/">
    <owl:Ontology rdf:about="http://www.co-ode.org/ontologies/pizza">
        <owl:versionIRI rdf:resource="http://www.co-ode.org/ontologies/pizza/2.0.0"/>
        <dc:title xml:lang="en">pizza</dc:title>
        <terms:contributor>Nick Drummond</terms:contributor>
        <terms:license rdf:datatype="http://www.w3.org/2001/XMLSchema#string">Creative Commons Attribution 3.0 (CC BY 3.0)</terms:license>
        <rdfs:label rdf:datatype="http://www.w3.org/2001/XMLSchema#string">pizza</rdfs:label>
        <terms:provenance xml:lang="en">v2.0 Added new annotations to the ontology using standard/well-know annotation properties

v1.5. Removed protege.owl import and references. Made ontology URI date-independent

v1.4. Added Food class (used in domain/range of hasIngredient), Added several hasCountryOfOrigin restrictions on pizzas, Made hasTopping invers functional</terms:provenance>
        <owl:versionInfo rdf:datatype="http://www.w3.org/2001/XMLSchema#string">2.0</owl:versionInfo>
        <terms:contributor>Alan Rector</terms:contributor>
        <dc:description xml:lang="en">An ontology about pizzas and their toppings.

This is an example ontology that contains all constructs required for the various versions of the Pizza Tutorial run by Manchester University (see http://owl.cs.manchester.ac.uk/publications/talks-and-tutorials/protg-owl-tutorial).</dc:description>
        <terms:contributor>Matthew Horridge</terms:contributor>
        <terms:contributor>Chris Wroe</terms:contributor>
        <terms:contributor>Robert Stevens</terms:contributor>
    </owl:Ontology>
"""

#%% md

## Constructing an ontology from Scratch

#%%

from rdflib import Namespace, Literal, Graph
from funowl import SubObjectPropertyOf, InverseObjectProperties, FunctionalObjectProperty, \
    InverseFunctionalObjectProperty, ObjectPropertyDomain, ObjectPropertyRange, SubClassOf
from funowl.annotations import AnnotationValue

from funowl.ontology_document import OntologyDocument, Ontology

DC = Namespace("http://purl.org/dc/elements/1.1/")
TERMS = Namespace("http://purl.org/dc/terms/")
PIZZA = Namespace("http://www.co-ode.org/ontologies/pizza#")

pizza_doc = OntologyDocument()
pizza_doc.prefixes(PIZZA, dc=DC, terms=TERMS)
pizza = Ontology("http://www.co-ode.org/ontologies/pizza",
                 "http://www.co-ode.org/ontologies/pizza/2.0.0")
pizza_doc.ontology = pizza
pizza.annotation(DC.title, "pizza")
pizza.annotation(TERMS.contributor, "Alan Rector")
pizza.annotation(TERMS.contributor, "Matthew Horridge")
pizza.annotation(TERMS.contributor, "Chris Wroe")
pizza.annotation(TERMS.contributor, "Robert Stevens")
pizza.annotation(DC.description,
                 AnnotationValue(Literal("""An ontology about pizzas and their toppings.

This is an example ontology that contains all constructs required for the various versions of the Pizza Tutorial
 run by Manchester University 
 (see http://owl.cs.manchester.ac.uk/publications/talks-and-tutorials/protg-owl-tutorial).""", lang="en")))
pizza.axioms.append(SubObjectPropertyOf(PIZZA.hasBase, PIZZA.hasIngredient))
pizza.axioms.append(InverseObjectProperties(PIZZA.hasBase, PIZZA.isBaseOf))
pizza.axioms.append(FunctionalObjectProperty(PIZZA.hasBase))
pizza.axioms.append(InverseFunctionalObjectProperty(PIZZA.hasBase))
pizza.axioms.append(ObjectPropertyDomain(PIZZA.hasBase, PIZZA.Pizza))
pizza.axioms.append(ObjectPropertyRange(PIZZA.hasBase, PIZZA.PizzaBase))

print(pizza_doc.to_functional().getvalue())


#%% md

## Ontologies in functional format can be read from files or URL's

#%%
from funowl.converters.functional_converter import to_python
from funowl.writers.FunctionalWriter import FunctionalWriter

pizza_doc = to_python("https://raw.githubusercontent.com/hsolbrig/funowl/master/tests/data/pizza.owl")
w = FunctionalWriter(g=pizza_doc.add_namespaces(Graph()))
for axiom in pizza_doc.ontology.axioms:
    if isinstance(axiom, SubClassOf) and str(axiom.subClassExpression) == 'pizza:AmericanHot':
        w.add(axiom)
print(str(w))

