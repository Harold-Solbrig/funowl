from typing import Dict, Tuple, List
from funowl import SubClassOf, EquivalentClasses, Annotation
from funowl.axioms import Axiom
from funowl.class_expressions import ClassExpression, ObjectIntersectionOf
from funowl.converters.functional_converter import to_python
owl_functional = """
Prefix(:=<https://loinc.org/document_ontology/>)
Prefix(owl:=<http://www.w3.org/2002/07/owl#>)
Prefix(rdf:=<http://www.w3.org/1999/02/22-rdf-syntax-ns#>)
Prefix(xml:=<http://www.w3.org/XML/1998/namespace>)
Prefix(xsd:=<http://www.w3.org/2001/XMLSchema#>)
Prefix(obda:=<https://w3id.org/obda/vocabulary#>)
Prefix(rdfs:=<http://www.w3.org/2000/01/rdf-schema#>)
Prefix(document_ontology:=<https://loinc.org/document_ontology/#>)
Prefix(untitled-ontology-17:=<https://loinc.org/dmbaorto/ontologies/2019/5/untitled-ontology-17#>)


Ontology(<https://loinc.org/document_ontology/>

AnnotationAssertion(rdfs:label <https://loinc.org/document_ontology/#93024-8> "Pharmacist Consult note (D)"^^xsd:string)
AnnotationAssertion(document_ontology:hasCode <https://loinc.org/document_ontology/#93024-8> "93024-8"^^xsd:string)
SubClassOf(<https://loinc.org/document_ontology/#93024-8> document_ontology:Loincs)
SubClassOf(<https://loinc.org/document_ontology/#93024-8> ObjectSomeValuesFrom(document_ontology:document-kind document_ontology:LP173418-7))
SubClassOf(<https://loinc.org/document_ontology/#93024-8> ObjectSomeValuesFrom(document_ontology:document-role document_ontology:LP181523-4))
SubClassOf(<https://loinc.org/document_ontology/#93024-8> ObjectSomeValuesFrom(document_ontology:document-type-of-service document_ontology:LP173110-0))
)
"""

ontologydoc = to_python(owl_functional)

equivalents: Dict[ClassExpression, List[Axiom]] = dict()

# Convert all subclass expressions into the equivalents
for axiom in ontologydoc.ontology.axioms:
    # Note that we can't use isinstance because of type cooercion
    if issubclass(type(axiom), SubClassOf):
        equivalents.setdefault(axiom.subClassExpression, []).append(axiom)

for class_expression, axioms in equivalents.items():
    if len(axioms) == 1:
        ontologydoc.ontology.equivalentClasses(class_expression,
                                   axioms[0].superClassExpression)
    else:
        ontologydoc.ontology.equivalentClasses(class_expression,
                                   ObjectIntersectionOf(*[axiom.superClassExpression for axiom in axioms]))
    for axiom in axioms:
        ontologydoc.ontology.axioms.remove(axiom)


print(ontologydoc.to_functional().getvalue())