# Issues and problems with the OwL 2 test cases

## General Issues

1) Should we emit `owl:Thing a owl:Class`?  The spec doesn't appear to say we shouldn't, but the test cases themselves
are inconsistent.  `Bnode2somevaluesfrom.func` shows it as not being emitted, yet other tests do.  For the time being,
identifiers.py#43 does not emit any declarations about XSD, RDF, RDFS or OWL, and our tests remove them (with warnings)
from the target files.

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

The Finland converter got the properties backward -- sb `hasName disjointWith hasAddress`

**New/Feature/Keys/002.func**
**Validating New/Feature/ObjectQCR/001.func**
**Validating New/Feature/ObjectQCR/002.func**
**Owl2/rl/rules/fp/differentFrom.fun**
**Owl2/rl/rules/ifp/differentFrom.func**

The Finland converter records a pair as `allDifferent` rather than `differentFrom`