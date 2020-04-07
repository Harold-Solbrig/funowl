# Issues and problems with the OwL 2 test cases

## General Issues

1. Should we emit `owl:Thing a owl:Class`?  The spec doesn't appear to say we shouldn't, but the test cases themselves
are inconsistent.  `Bnode2somevaluesfrom.func` shows it as not being emitted, yet other tests do.  For the time being,
identifiers.py#43 does not emit any declarations about XSD, RDF, RDFS or OWL, and our tests remove them (with warnings)
from the target files.

2. Reified annotations: the Finland parser and, possibly, the test case itself replicates BNodes used as `annotatedSource`
or `annotatedTarget` elements.  Using
[FS2RDF/propertychain/2/annotated/ar.func](tests/test_owls2_test_suite/FS2RDF/propertychain/2/annotated/ar.func) as an example,
we can either point at a _copy_ of the subject and object in the annotation Axiom:
    ```text
    <http://example.org/p> a :ObjectProperty ;
        :propertyChainAxiom ( <http://example.org/q> <http://example.org/r> ) .
    
    [] a :Axiom ;
        rdfs:comment "I hereby annotate this" ;
        :annotatedProperty :propertyChainAxiom ;
        :annotatedSource <http://example.org/p> ;
        :annotatedTarget ( <http://example.org/q> <http://example.org/r> ) .
    ```
   or we can point at the items themselves:
    ```text
    <http://example.org/p> a :ObjectProperty ;
        :propertyChainAxiom _:fb1b444ef721943fd96f22d4d6c53d9b1b1 .
    
    [] a :Axiom ;
        rdfs:comment "I hereby annotate this" ;
        :annotatedProperty :propertyChainAxiom ;
        :annotatedSource <http://example.org/p> ;
        :annotatedTarget _:fb1b444ef721943fd96f22d4d6c53d9b1b1 .
    
    _:fb1b444ef721943fd96f22d4d6c53d9b1b2 rdf:first <http://example.org/r> ;
        rdf:rest () .
    
    _:fb1b444ef721943fd96f22d4d6c53d9b1b1 rdf:first <http://example.org/q> ;
        rdf:rest _:fb1b444ef721943fd96f22d4d6c53d9b1b2 .
    ```
    The first form is obviously more readable, but it is inconsistent but will be a real challenge to process, as
    one has to go on the assumption that `_:b1 a rdf:Thing . _:b2 a rdf:Thing` implies `_:b1` == `_:b2`, something
    that I suspect runs counter to the RDF philosophy.

    Since the test cases use the first form, we have added an option `USE_BNODE_COPIES` to funowl/base/clone_subgraph.py to
    allow us to have it either way.

3. `sameIndividuals` annotations
The RDF spec seems to have a gap when it comes to how annotations apply to
`sameIndividuals(Annotation(rdfs:comment "annot") :a :b :c :d).  The Finnish converter seems to
interpret this as
   ```text
   [] a :Axiom ;
    rdfs:comment "annot" ;
    :annotatedProperty :sameAs ;
    :annotatedSource :a, :b, :c ;
    :annotatedTarget :b, :c, :d .
    ```
    Not sure quite what to think of this, but for the time being we're going
    to go with it.

4. ObjectPropertyChain
Does `ObjectPropertyChain(:p1 :p2)` imply `:p1 a owl:ObjectProperty` and `:p2 a owl:ObjectProperyt`?
The generator currently emits them, but the test code (Rdfbased/sem/chain/def.func) does not show this as happening.  For the
moment we are going to assume that we are right and change the test targets:
   * Rdfbased/sem/chain/def.ttl
   * Owl2/rl/rules/ifp/askey.ttl
   * TestCase-WebOnt/I5.1/001.ttl
   * Rdfbased/sem/chain/def.ttl
   * Rdfbased/sem/key/def.ttl
   * Rdfbased/sem/ndis/alldisjointproperties/fw.ttl

5. HasKey
Does `HasKey(ex:c () (ex:p1 ex:p2))` imply `ex:p1 a owl:DatatypeProperyt`?  Same as ObjectPropertyChain.  
see: Rdfbased/sem/key/def.func and Rdfbased/sem/ndis/alldisjointproperties/fw.func

6. Representation of quoted strings inside triple-quoted strings:
   * TestCase-WebOnt/I5.8/013.func
   * TestCase-WebOnt/I5.8/015.func

   Expected:
   ```text
   <http://example.org/user/data#type> rdfs:comment """
   This type maps the string "foo" to the number 3.
   All other strings are not in the lexical space.
   """ .
   ```

   FunOWL
   ```text
   <http://example.org/user/data#type> rdfs:comment """
   This type maps the string \\"foo\\" to the number 3.
   All other strings are not in the lexical space.
  """ .
  ```
  As a short-term solution, we have added the escapes to the expected side of things

## Specific file issues

**Direct_Semantics_Literal_disjoint_from_Thing.func**

There is a conversion error on the Finland site, where `EquivalentClasses(owl:Thing ObjectOneOf(:b :a))` gets converted
into:
```text
owl:Thing owl:equivalentClass [ a owl:Class ;
            owl:oneOf ( example:a example:b ) ] .
```

**FS2RDF/different/individuals/2/annotation/ar.func**

The test case has two errors:
1) `DifferentIndividuals(Annotation(rdfs:comment "I hereby annotate this") :a :b))` should map to:
    ```text
    <http://example.org/a> a :NamedIndividual ;
        :differentFrom <http://example.org/b> .
    ```
    instead of `allDifferent` and
2) The annotations were dropped.

**FS2RDF/different/individuals/2/ar.func**
`DifferentIndividuals(:a :b))` should map to:
    ```text
    <http://example.org/a> a :NamedIndividual ;
        :differentFrom <http://example.org/b> .
    ```
    instead of `allDifferent`
    
**FS2RDF/disjoint/classes/2/annotation/ar.func**

The annotation axiom was repeated twice.  Error in Finland converter.

**FS2RDF/domain/range/expression/ar.func**

```text
    Declaration(DataProperty(:p5))
    Declaration(Class(:c4))
    ObjectPropertyDomain(ObjectInverseOf(:p5) :c4)
```

    InverseObjectProperty := 'ObjectInverseOf' '(' ObjectProperty ')'
    
The results of this test indicate that `:p5` should be declared as _both_ an ObjectProperty and a DataProperty.  This
is an outstanding issue in the parser

**FS2RDF/equivalent/classes/2/annotation/ar.func**

The annotation axiom was repeated twice.  Error in Finland converter.

**FS2RDF/equivalent/classes/3/annotation/ar.func**

The annotation axiom was repeated twice.  Error in Finland converter.


**FS2RDF/literals/ar.func**

Finland converter failed to return anything.  Probably choked on some of the embedded XML

Python tooling is unable to differentiate between `"1.0"^^<http://www.w3.org/2001/XMLSchema#decimal> ` and
`"1"^^<http://www.w3.org/2001/XMLSchema#decimal> `.  The test has temporarily been added to the skip list until
we can determine

**FS2RDF/same/individual/2/annotation/ar.func**

The annotation axiom was repeated twice.  Error in Finland converter.

**FS2RDF/same/individual/3/annotation/ar.func**

The annotation axiom was repeated multiple times.  Error in Finland converter.

**New/Feature/DisjointDataProperties/001.func**
**TestCase-WebOnt/disjointWith/008.func**
**TestCase-WebOnt/disjointWith/009.func**

The Finland converter got the properties backward -- sb `hasName disjointWith hasAddress`
Same with 008

**New/Feature/Keys/002.func**
**Validating New/Feature/ObjectQCR/001.func**
**Validating New/Feature/ObjectQCR/002.func**
**Owl2/rl/rules/fp/differentFrom.fun**
**Owl2/rl/rules/ifp/differentFrom.func**
**Rdfbased/sem/eqdis/different/sameas.func**
**TestCase-WebOnt/description/logic/501.func**
**TestCase-WebOnt/maxCardinality/001.func**
**TestCase-WebOnt/differentFrom/001.func**
**TestCase-WebOnt/description/logic/502.func**

The Finland converter records a pair as `allDifferent` rather than `differentFrom`

Note that maxCardinality/001.func was missing the ontology declaration as
well

**New/Feature/AnnotationAnnotations/001.func**

The annotation on the annotation wasn't emitted by the Finland processor

**Rdfbased/sem/eqdis/disclass/irrflxv.func**

Failed the Finland conversion completely.  ttl added on our side

**Rdfbased/sem/npa/dat/fw.func**

This test uses a non-standard OWL property -- `owl:targetValue` .  Our current
implementation does not emit declarations about the OWL, RDF or other known
namespaces, so this doesn't get emitted.  We are ignoring this test for the
time being.

**TestCase-WebOnt/I5.26/004.func**
**TestCase-WebOnt/I5.26/005.func**

The Finnish converter reversed the order of the declaration going from
XML to functional and then switched it again going to turtle.  Edited
the functional declaration to match the XML.

**TestCase-WebOnt/I5.3/009.func**
Finnish conversion failed -- loaded expected with output of generator.

**TestCase-WebOnt/miscellaneous/002.func**
Several implied declarations were missing -- not sure why.

**TestCase-WebOnt/I5.8/017.func**
Uses document local URI's -- funowl processor doesn't work with fragments (e.g. `"01"^^<#bar> .`)

**TestCase-WebOnt/I6.1/001.func**
The BNode elements of the test were missing completely.

**TestCase-WebOnt/imports/001.func**
**TestCase-WebOnt/imports/003.func**
**TestCase-WebOnt/imports/006.func**
**TestCase-WebOnt/imports/007.func**
**TestCase-WebOnt/imports/011.func**
All of these curiously miss one triple -- either `<http://www.w3.org/2002/03owlt/imports/support001-A#Man> a <http://www.w3.org/2002/07/owl#Class> .`
`<http://www.w3.org/2002/03owlt/imports/imports006#c> a <http://www.w3.org/2002/07/owl#Class> .` or
`<http://www.w3.org/2002/03owlt/imports/imports007#p> a <http://www.w3.org/2002/07/owl#ObjectProperty> .`

**TestCase-WebOnt/disjointWith/010.func**
Finnish conversion failed -- loaded with output of generator

**FS2RDF/ontology/annotation/annotation/ar.func**
Finnish loader didn't get the annotations correct.  Added our output