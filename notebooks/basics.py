import rdflib
from rdflib import Namespace, RDFS

from funowl.annotations import AnnotationAssertion
from funowl.ontology_document import Ontology

DC = Namespace("http://purl.org/dc/elements/1.1/")
TERMS = Namespace("http://purl.org/dc/terms/")
PIZZA = Namespace("http://www.co-ode.org/ontologies/pizza/pizza.owl#")

pizza = Ontology(iri="http://www.co-ode.org/ontologies/pizza",
                 version="http://www.co-ode.org/ontologies/pizza/2.0.0")
pizza.prefixes(**dict(dc=DC, terms=TERMS))
pizza.annotation(DC.title, rdflib.Literal("pizza", lang='en'))
pizza.annotation(TERMS.contributor, "Alan Rector")
pizza.annotation(TERMS.contributor, "Matthew Horridge")
pizza.annotation(TERMS.contributor, "Chris Wroe")
pizza.annotation(TERMS.contributor, "Robert Stevens")
pizza.annotation(DC.description,
                 """"An ontology about pizzas and their toppings.

This is an example ontology that contains all constructs required for the various versions of the Pizza Tutorial run by Manchester University (see http://owl.cs.manchester.ac.uk/publications/talks-and-tutorials/protg-owl-tutorial)."@en""")
pizza.subClassOf(PIZZA.American, PIZZA.NamedPizza)
pizza.subObjectPropertyOf(PIZZA.hasBase, PIZZA.hasIngredient)
pizza.inverseObjectProperties(PIZZA.hasBase, PIZZA.isBaseOf)
pizza.functionalObjectProperty(PIZZA.hasBase)
pizza.inverseFunctionalObjectProperty(PIZZA.hasBase)
pizza.objectPropertyDomain(PIZZA.hasBase, PIZZA.pizza)
pizza.objectPropertyRange(PIZZA.hasbase, PIZZA.PizzaBase)

pizza.axioms.append(
    AnnotationAssertion(RDFS.comment, PIZZA.hasIngredient,
                        '"NB Transitive - the ingredients of ingredients are ingredients of the whole"@en'))

print(pizza.to_functional().getvalue())