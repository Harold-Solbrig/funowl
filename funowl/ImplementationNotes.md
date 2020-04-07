# Implementation Notes

## Configuration parameters
### `funowl.base.clone_subgraph.USE_BNODE_COPIES`
This parameter controls whether subgraphs are cloned when they appear as `AnnotationAssertion` subjects or objects. The basic issue
is whether, when you are using the reification model in the [OWL AnnotationAssertion](https://www.w3.org/TR/owl2-syntax/#Annotation_Assertion), 
should BNodes be referenced directly or replicated.  When replicated directly, it is considerably easier to determine
which assertion that the Annotation applies to:

When duplicated, the resulting RDF is easier to understand, but one has to actually *compare* BNode content to determine
which statement the annotation applies to. As an example, [tests/test_owl2_test_suite/FS2RDF/ontology/annotation/annotation/ar.func]()
includes the statement:
    
     Ontology(Annotation(Annotation(:member :a) Annotation(:member :b) Annotation(:member :c) :for :eqc)

The *test* code (as interpreted by the [Finnish Converter](http://www.ldf.fi/service/owl-converter/)) produces two 
BNodes, one that carries the ontology assertion and a second for the annotation:
```turtle
@prefix : <http://example.org/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

_:b1 a owl:Ontology ;
   :for :eqc .

_:b2 a owl:Annotation ;
    :member :a, :b, :c ;
    owl:annotatedSource _:b3 ;
    owl:annotatedProperty :for ;
    owl:annotatedTarget :eqc .

_:b3 a owl:Ontology ;
     :for :eqc .
```

Setting `USE_BNODE_COPIES` to `False` yields the following:
```turtle
@prefix : <http://example.org/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

_:b1 a owl:Ontology ;
   :for :eqc .

_:b2 a owl:Annotation ;
    :member :a, :b, :c ;
    owl:annotatedSource _:b1 ;
    owl:annotatedProperty :for ;
    owl:annotatedTarget :eqc .
```

The default setting, at the moment is `True`