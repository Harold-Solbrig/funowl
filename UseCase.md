# Sample Use Case

Start with an ontology that has been built using entirely `SubClassOf` declarations.

Example:
```
AnnotationAssertion(rdfs:label <https://loinc.org/document_ontology/#93024-8> "Pharmacist Consult note (D)"^^xsd:string)
AnnotationAssertion(document_ontology:hasCode <https://loinc.org/document_ontology/#93024-8> "93024-8"^^xsd:string)
SubClassOf(<https://loinc.org/document_ontology/#93024-8> document_ontology:Loincs)
SubClassOf(<https://loinc.org/document_ontology/#93024-8> ObjectSomeValuesFrom(document_ontology:document-kind document_ontology:LP173418-7))
SubClassOf(<https://loinc.org/document_ontology/#93024-8> ObjectSomeValuesFrom(document_ontology:document-role document_ontology:LP181523-4))
SubClassOf(<https://loinc.org/document_ontology/#93024-8> ObjectSomeValuesFrom(document_ontology:document-type-of-service document_ontology:LP173110-0))
```

The goal is to convert _selected_ nodes into "fully defined entries":

```
# AnnotationAssertion(rdfs:label <https://loinc.org/document_ontology/#93024-8> "Pharmacist Consult note (D)"^^xsd:string)
AnnotationAssertion(document_ontology:hasCode <https://loinc.org/document_ontology/#93024-8> "93024-8"^^xsd:string)
EquivalentClasses(<https://loinc.org/document_ontology/#93024-8> ObjectIntersectionOf(document_ontology:Loincs ObjectSomeValuesFrom(document_ontology:document-kind document_ontology:LP173418-7) ObjectSomeValuesFrom(document_ontology:document-role document_ontology:LP181523-4) ObjectSomeValuesFrom(document_ontology:document-type-of-service document_ontology:LP173110-0)))
```

The filter man be reasonably complex and  cannot be specified lexically (as a sed script).



