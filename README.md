![Owl in a bucket](images/owlinbucket.jpg)

[![Pyversions](https://img.shields.io/pypi/pyversions/funowl.svg)](https://pypi.python.org/pypi/funowl)
[![PyPi](https://img.shields.io/pypi/v/funowl.svg)](https://pypi.python.org/pypi/funowl)
![Build](https://github.com/hsolbrig/funowl/workflows/Build/badge.svg)
![Publish](https://github.com/hsolbrig/funowl/workflows/Publish%20Python%20Package/badge.svg)


# FunOwl - Functional OWL syntax for Python
[OWL2 Functional Style Syntax](https://www.w3.org/TR/owl2-syntax/) for python.

## Goals
To date, it appears that the majority of the python based OWL generators use variations of the 
[OWL RDF syntax](https://www.w3.org/TR/2012/REC-owl2-mapping-to-rdf-20121211/) -- something that is time consuming and
error prone.  What we are attempting to do in this project is (in order of relative priority): 

1) Provide a pythonic API that follows the OWL functional model for constructing OWL
2) Emit OWL in OWL Functional syntax
3) Emit OWL in RDF (any rdflib flavor)
4) Consume OWL functional syntax
5) Consume OWL RDF
6) Provide a [py4j](https://www.py4j.org/) or equivalent wrapper to the standard Java OWL libraries

### Goal 1: Create OWL Functional Syntax using Python
```python
from rdflib import RDFS, OWL, Namespace
from funowl import OntologyDocument, Ontology

EX = Namespace("http://www.example.com/ontology1#")

o = Ontology("http://www.example.com/ontology1")
o.imports("http://www.example.com/ontology2")
o.annotation(RDFS.label, "An example")
o.subClassOf(EX.Child, OWL.Thing)
doc = OntologyDocument(EX, o)
print(str(doc))
```
### Output
```
Prefix( xml: = <http://www.w3.org/XML/1998/namespace> )
Prefix( rdf: = <http://www.w3.org/1999/02/22-rdf-syntax-ns#> )
Prefix( rdfs: = <http://www.w3.org/2000/01/rdf-schema#> )
Prefix( xsd: = <http://www.w3.org/2001/XMLSchema#> )
Prefix( owl: = <http://www.w3.org/2002/07/owl#> )
Prefix( : = <http://www.example.com/ontology1#> )

Ontology( <http://www.example.com/ontology1>
    Import( <http://www.example.com/ontology2> )
    Annotation( rdfs:label "An example" )
    SubClassOf( :Child owl:Thing )
)
```
Represent:
```
Prefix(:=<http://example.org/>)
Prefix(xsd:=<http://www.w3.org/2001/XMLSchema#>)
Ontology(
  Declaration(NamedIndividual(:a))
  Declaration(DataProperty(:dp))
  Declaration(Class(:A))
  SubClassOf(:A DataAllValuesFrom(:dp 
    DataOneOf("3"^^xsd:integer "4"^^xsd:int))
  ) 
  SubClassOf(:A DataAllValuesFrom(:dp 
    DataOneOf("2"^^xsd:short "3"^^xsd:int))
  )
  ClassAssertion(:A :a)
  ClassAssertion(DataSomeValuesFrom(:dp 
    DataOneOf("3"^^xsd:integer)) :a
  )
)
```

As:
```python 
from rdflib import Namespace, XSD, OWL, Literal
from funowl import *

EX = Namespace("http://example.org/")

# Ontology represents the OWLF OntologyDocument production
o = Ontology(EX.myOntology, "http://example.org/myOntolology/version/0.1")

# prefixes array includes default
o.prefixes(EX, rdfs=RDFS)
o.prefixes.append(owl=OWL)

# namedIndividual, objectProperty, class, et. properties add to declarations
o.namedIndividual(EX.a)

# Declarations can also be added explicitly
o.declarations(DataProperty(EX.dp), Class(EX.A))

# Axioms are added by type
o.subClassOf(EX.A, DataAllValuesFrom(EX.dp, DataOneOf(3, Literal(4, datatype=XSD.int_))))

# or as an array
o.axioms.append(SubClassOf(EX.A, DataAllValuesFrom(EX.dp, DataOneOf(Literal(2, datatype=XSD.short), Literal(3, datatype=XSD.int_))))
o.class(EX.A, EX.a)
o.class(DataSomeValuesFrom(EX.dp, DataOneOf(3)), EX.a)

print(str(o))
```
```text
Prefix(:=<http://example.org/>)
Prefix(xsd:=<http://www.w3.org/2001/XMLSchema#>)
Prefix(owl:=<http://www.w3.org/2002/07/owl#>)
Ontology( 
  Declaration(NamedIndividual(:a))
  Declaration(DataProperty(:dp))
  Declaration(Class(:A))
  SubClassOf(:A DataAllValuesFrom(:dp 
    DataOneOf("3"^^xsd:integer "4"^^xsd:int))
  ) 
  SubClassOf(:A DataAllValuesFrom(:dp 
    DataOneOf("2"^^xsd:short "3"^^xsd:int))
  )
  ClassAssertion(:A :a)
  ClassAssertion(DataSomeValuesFrom(:dp 
    DataOneOf("3"^^xsd:integer)) :a
  )
)
```

## Transforming Functional Syntax to RDF
See: [test_issue_57.py](tests/test_issues/test_issue_57.py) for full example
```python
from rdflib import Graph
from funowl.converters.functional_converter import to_python

# The functional syntax input can be a string, URL, file loc or open file
function_pizza = "https://github.com/Harold-Solbrig/funowl/blob/main/tests/data/pizza.owl"
internal_pizza = to_python(function_pizza)

# Emit the internal representation as an rdflib graph
g = Graph()
internal_pizza.to_rdf(g)

# Serialize the rdflib graph in your favorite format
print(g.serialize(format="ttl"))
```

## Command Line Interface
`funowl` can be installed with either `pip` or `pipenv`.  

```shell
> funowl -h 
usage: funowl [-h]
              [-f {ttl,hext,json-ld,longturtle,n3,nquads,nt,nt11,ntriples,pretty-xml,trig,trix,ttl,turtle,xml}]
              [-np]
              input [output]

Convert OWL Functional Syntax to RDF

positional arguments:
  input                 Input OWL functional syntax. Can be a file name or URL
  output                Output file. If omitted, output goes to stdout

options:
  -h, --help            show this help message and exit
  -f {ttl,hext,json-ld,longturtle,n3,nquads,nt,nt11,ntriples,pretty-xml,trig,trix,ttl,turtle,xml}, --format {ttl,hext,json-ld,longturtle,n3,nquads,nt,nt11,ntriples,pretty-xml,trig,trix,ttl,turtle,xml}
                        Output RDF Format. If omitted, guess from output file
                        suffix. If guessing doesn't work, assume 'turtle'
  -np, --noProgressBar  Don't output the progress indicators
```

To convert an OWL functional representation of the pizza ontology to RDF:
```shell
> funowl https://raw.githubusercontent.com/Harold-Solbrig/funowl/main/tests/data/pizza.owl
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix pizza: <http://www.co-ode.org/ontologies/pizza/pizza.owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix terms: <http://purl.org/dc/terms/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

dc:description a owl:AnnotationProperty .

dc:title a owl:AnnotationProperty .

terms:contributor a owl:AnnotationProperty .

terms:license a owl:AnnotationProperty .

terms:provenance a owl:AnnotationProperty .

<http://www.co-ode.org/ontologies/pizza> a owl:Ontology ;
    rdfs:label "pizza"^^xsd:string ;
    dc:description """An ontology about pizzas and their toppings.
      ...
```
To convert the same ontology into XML, either:

`funowl https://raw.githubusercontent.com/Harold-Solbrig/funowl/main/tests/data/pizza.owl -f xml > pizza.xml`
   
or

`funowl https://raw.githubusercontent.com/Harold-Solbrig/funowl/main/tests/data/pizza.owl pizza.xml`

```shell
> cat pizza.xml
<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:owl="http://www.w3.org/2002/07/owl#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
   xmlns:skos="http://www.w3.org/2004/02/skos/core#"
   xmlns:terms="http://purl.org/dc/terms/"
>
  <rdf:Description rdf:nodeID="Nd1a614092c234a3b90971238bb6550e8">
    <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Restriction"/>
    <owl:onProperty rdf:resource="http://www.co-ode.org/ontologies/pizza/pizza.owl#hasTopping"/>
    <owl:someValuesFrom rdf:resource="http://www.co-ode.org/ontologies/pizza/pizza.owl#TomatoTopping"/>
  </rdf:Description>
      ...
      
</rdf:RDF>
```

## Other packages

While we would be happy to be corrected, to the best of our knowledge there is to be minimal support for OWL in python.
* [OwlReady2](https://owlready2.readthedocs.io/en/latest/) appears to be the closest thing to what we are 
looking for, but, as described in this [paper](http://www.lesfleursdunormal.fr/static/_downloads/article_owlready_aim_2017.pdf)
it creates an ontology-oriented programming API for ontologies, while what we want is much closer to the raw OWL itself. 
We have also recently discovered 
* The `rdflib` [infixowl](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.extras.html#module-rdflib.extras.infixowl) 
actually comes closer to what we've been trying to accomplish and, had we known of its existence before we got started, we
may have chosen to build on it instead of starting from scratch.
