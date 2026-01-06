# Migration Guide: funowl to py-horned-owl

This guide documents how to migrate Python code from [funowl](https://github.com/hsolbrig/funowl) to [py-horned-owl](https://github.com/ontology-tools/py-horned-owl).

## Why Migrate?

**funowl** is a pure Python implementation of OWL2 Functional Syntax that is no longer actively maintained.

**py-horned-owl** is a PyO3 binding to the Rust-based [horned-owl](https://github.com/phillord/horned-owl) library, offering:

- **Performance**: Rust-based parsing and serialization is significantly faster
- **Active maintenance**: Regular releases and bug fixes
- **Multiple formats**: Supports OWL/XML (`.owl`), OWL-XML (`.owx`), OWL Functional (`.ofn`), and RDF/XML
- **OWL2 conformance**: Well-tested against OWL2 specification
- **Modern API**: Pythonic operators for building class expressions (`A & B`, `A | B`, `~A`)

## Installation

```bash
# Remove funowl
pip uninstall funowl

# Install py-horned-owl
pip install py-horned-owl
```

## Import Changes

```python
# funowl
from funowl import (
    OntologyDocument, Ontology, IRI, Class, ObjectProperty,
    SubClassOf, EquivalentClasses, ObjectSomeValuesFrom,
    ObjectIntersectionOf, ObjectUnionOf, Declaration, Prefix,
    Literal, Annotation, AnnotationAssertion, AnnotationProperty
)
from funowl.converters.functional_converter import to_python

# py-horned-owl
import pyhornedowl
from pyhornedowl.model import (
    IRI, Class, ObjectProperty, SubClassOf, EquivalentClasses,
    ObjectSomeValuesFrom, ObjectIntersectionOf, ObjectUnionOf,
    DeclareClass, DeclareObjectProperty, SimpleLiteral, DatatypeLiteral,
    Annotation, AnnotationAssertion, AnnotationProperty, AnnotatedComponent
)
```

## Creating an Ontology

### funowl

```python
from funowl import OntologyDocument, Ontology, Prefix

ontology = Ontology("http://example.org/my-ontology")
doc = OntologyDocument("http://example.org/my-ontology", ontology)
doc.prefixDeclarations.append(Prefix("ex", "http://example.org/"))
```

### py-horned-owl

```python
import pyhornedowl

ontology = pyhornedowl.PyIndexedOntology()
ontology.add_prefix_mapping("ex", "http://example.org/")
# Note: Ontology IRI is set differently or when saving
```

## Prefixes, CURIEs, and IRI Resolution

This section covers the different ways to handle prefixes and compact IRIs in both libraries.

### Declaring Prefixes

#### funowl

```python
from funowl import OntologyDocument, Ontology, Prefix

doc = OntologyDocument("http://example.org/ont", Ontology("http://example.org/ont"))

# Named prefix (ex:)
doc.prefixDeclarations.append(Prefix("ex", "http://example.org/"))

# Default/empty prefix (:)
doc.prefixDeclarations.append(Prefix("", "http://example.org/default/"))

# Standard prefixes are added automatically (owl:, rdf:, rdfs:, xsd:, xml:)
```

#### py-horned-owl

```python
import pyhornedowl

ontology = pyhornedowl.PyIndexedOntology()

# Named prefix (ex:)
ontology.add_prefix_mapping("ex", "http://example.org/")

# Default/empty prefix (:) - used for :LocalName and bare LocalName
ontology.add_prefix_mapping("", "http://example.org/default/")

# Access prefix mappings
prefix_map = ontology.prefix_mapping
```

### CURIE Styles: `ex:Foo`, `:Foo`, and `Foo`

Both libraries support different CURIE (Compact URI) styles, but handle them differently.

#### funowl - CURIEs are Preserved as Strings

funowl treats CURIEs as opaque strings and relies on rdflib `Namespace` for expansion:

```python
from funowl import Class, SubClassOf
from rdflib import Namespace

EX = Namespace("http://example.org/")
DEFAULT = Namespace("http://example.org/default/")

# Using rdflib Namespace (recommended - expands immediately)
cls_a = Class(EX.A)           # → http://example.org/A
cls_b = Class(DEFAULT.B)      # → http://example.org/default/B

# Using string CURIEs (NOT expanded - stored as-is)
cls_x = Class("ex:X")         # → stored as "ex:X" (not expanded!)
cls_y = Class(":Y")           # → stored as ":Y" (not expanded!)

# The serializer uses prefix declarations to shorten full IRIs
# Full IRI http://example.org/A → serializes as ex:A
# Full IRI http://example.org/default/B → serializes as :B
```

#### py-horned-owl - CURIEs are Expanded Immediately

py-horned-owl expands CURIEs to full IRIs when using factory methods:

```python
import pyhornedowl

ontology = pyhornedowl.PyIndexedOntology()
ontology.add_prefix_mapping("ex", "http://example.org/")
ontology.add_prefix_mapping("", "http://example.org/default/")

# Style 1: Full IRI
cls = ontology.clazz("http://example.org/A")
# Result: http://example.org/A

# Style 2: Prefixed CURIE (ex:Foo)
cls = ontology.clazz("ex:Foo")
# Result: http://example.org/Foo  (expanded!)

# Style 3: Default prefix CURIE (:Foo)
cls = ontology.clazz(":Foo")
# Result: http://example.org/default/Foo  (expanded!)

# Style 4: Bare local name (Foo) - uses default prefix
cls = ontology.clazz("Foo")
# Result: http://example.org/default/Foo  (expanded!)
```

### The `absolute` Parameter in py-horned-owl

py-horned-owl's factory methods have an `absolute` parameter to control IRI interpretation:

```python
ontology.add_prefix_mapping("", "http://example.org/")

# absolute=True (default for iri()) - treat as full IRI, no expansion
ontology.iri("Foo", absolute=True)        # → Foo (treated as full IRI!)

# absolute=False - treat as CURIE, expand using prefix mappings
ontology.iri("Foo", absolute=False)       # → http://example.org/Foo

# absolute=None (default for clazz, etc.) - auto-detect based on "://"
ontology.iri("Foo", absolute=None)        # → http://example.org/Foo (no "://")
ontology.iri("http://x.org/Foo", absolute=None)  # → http://x.org/Foo (has "://")

# Factory methods default to absolute=None (auto-detect)
ontology.clazz("Foo")                     # → http://example.org/Foo
ontology.clazz("ex:Bar")                  # → http://example.org/Bar
ontology.clazz("http://other.org/Baz")    # → http://other.org/Baz
```

### Using `curie()` vs `iri()` in py-horned-owl

```python
ontology.add_prefix_mapping("ex", "http://example.org/")
ontology.add_prefix_mapping("", "http://example.org/default/")

# curie() - always treats input as CURIE, always expands
ontology.curie("ex:A")      # → http://example.org/A
ontology.curie(":A")        # → http://example.org/default/A
ontology.curie("A")         # → http://example.org/default/A

# iri() - default is absolute=True, so no expansion
ontology.iri("ex:A")        # → ex:A (NOT expanded - probably not what you want!)
ontology.iri("ex:A", absolute=False)  # → http://example.org/A
```

### Serialization: How CURIEs Appear in Output

#### funowl

```python
from funowl import OntologyDocument, Ontology, Prefix, Class, SubClassOf, Declaration
from rdflib import Namespace

EX = Namespace("http://example.org/")
DEFAULT = Namespace("http://example.org/default/")

ontology = Ontology("http://example.org/ont")
doc = OntologyDocument("http://example.org/ont", ontology)
doc.prefixDeclarations.append(Prefix("ex", "http://example.org/"))
doc.prefixDeclarations.append(Prefix("", "http://example.org/default/"))

ontology.axioms.append(SubClassOf(Class(EX.A), Class(DEFAULT.B)))

print(str(doc))
```

Output:
```
Prefix( ex: = <http://example.org/> )
Prefix( : = <http://example.org/default/> )

Ontology( ex:ont
    SubClassOf( ex:A :B )
)
```

#### py-horned-owl

```python
import pyhornedowl
from pyhornedowl.model import SubClassOf, DeclareClass

ontology = pyhornedowl.PyIndexedOntology()
ontology.add_prefix_mapping("ex", "http://example.org/")
ontology.add_prefix_mapping("", "http://example.org/default/")

a = ontology.clazz("ex:A")    # http://example.org/A
b = ontology.clazz(":B")      # http://example.org/default/B

ontology.add_axiom(SubClassOf(a, b))
print(ontology.save_to_string("ofn"))
```

Output:
```
Prefix(ex:=<http://example.org/>)
Prefix(:=<http://example.org/default/>)
Ontology(    SubClassOf(ex:A B)
)
```

Note: py-horned-owl serializes default-prefix IRIs as bare local names (`B`) rather than `:B`. Both are valid OWL Functional Syntax.

### Parsing OFN with Prefixes

Both libraries require prefixes to be declared in the OFN string being parsed.

#### funowl

```python
from funowl.converters.functional_converter import to_python

ofn = '''
Prefix(ex:=<http://example.org/>)
Prefix(:=<http://example.org/default/>)
Ontology(<http://example.org/ont>
  SubClassOf(ex:A :B)
  SubClassOf(:B C)
)
'''

doc = to_python(ofn)

# funowl preserves CURIEs as-is (not expanded)
for ax in doc.ontology.axioms:
    print(ax)
# SubClassOf(subClassExpression=Class(v='ex:A'), superClassExpression=Class(v=':B'), ...)
# SubClassOf(subClassExpression=Class(v=':B'), superClassExpression=Class(v='C'), ...)
```

#### py-horned-owl

```python
import pyhornedowl

ofn = '''
Prefix(ex:=<http://example.org/>)
Prefix(:=<http://example.org/default/>)
Ontology(<http://example.org/ont>
  SubClassOf(ex:A :B)
  SubClassOf(:B C)
)
'''

ontology = pyhornedowl.open_ontology_from_string(ofn, "ofn")

# py-horned-owl expands all CURIEs to full IRIs
for ax in ontology.get_axioms():
    print(ax.component)
# SubClassOf with http://example.org/A, http://example.org/default/B
# SubClassOf with http://example.org/default/B, http://example.org/default/C
```

**Important**: py-horned-owl's parser requires ALL prefixes used in the OFN to be declared. An undeclared prefix causes a parse error:

```python
# This FAILS - "x:" prefix not declared
bad_ofn = '''
Ontology(<http://example.org/ont>
  SubClassOf(x:A x:B)
)
'''
# Raises: ValueError: Failed to open ontology: ParserError...
```

### Migration Pattern: CURIE Handling

When migrating, the key difference is:

| Aspect | funowl | py-horned-owl |
|--------|--------|---------------|
| CURIE in constructor | Stored as-is | Expanded immediately |
| Recommended approach | Use rdflib `Namespace` | Use factory methods with CURIEs |
| String "ex:Foo" | Stored as "ex:Foo" | Expanded to full IRI |
| String ":Foo" | Stored as ":Foo" | Expanded to full IRI |
| String "Foo" | Stored as "Foo" | Expanded using default prefix |

**funowl migration pattern:**
```python
# Before (funowl)
from rdflib import Namespace
EX = Namespace("http://example.org/")
cls = Class(EX.MyClass)

# After (py-horned-owl)
ontology.add_prefix_mapping("ex", "http://example.org/")
cls = ontology.clazz("ex:MyClass")  # or use full IRI
```

## Creating IRIs and Entities

### funowl

```python
from funowl import IRI, Class, ObjectProperty

# IRIs can be created from strings directly
iri = IRI("http://example.org/MyClass")

# Or used inline in constructors
cls = Class("http://example.org/MyClass")
prop = ObjectProperty("http://example.org/myProperty")
```

### py-horned-owl

```python
import pyhornedowl

ontology = pyhornedowl.PyIndexedOntology()
ontology.add_prefix_mapping("ex", "http://example.org/")

# Use factory methods on the ontology (recommended for caching)
iri = ontology.iri("http://example.org/MyClass")
cls = ontology.clazz("http://example.org/MyClass")
prop = ontology.object_property("http://example.org/myProperty")

# CURIEs work with prefix mappings
cls = ontology.clazz("ex:MyClass")  # Expands to full IRI

# Or create directly from model (no caching)
from pyhornedowl.model import IRI, Class
iri = IRI.parse("http://example.org/MyClass")
```

## Adding Axioms

### funowl

```python
from funowl import SubClassOf, Class

ontology.axioms.append(SubClassOf(
    Class("http://example.org/Child"),
    Class("http://example.org/Parent")
))
```

### py-horned-owl

```python
from pyhornedowl.model import SubClassOf

child = ontology.clazz("http://example.org/Child")
parent = ontology.clazz("http://example.org/Parent")
axiom = SubClassOf(child, parent)
ontology.add_axiom(axiom)
```

## N-ary Axioms (EquivalentClasses, DisjointClasses, etc.)

### funowl

```python
from funowl import EquivalentClasses, Class

# Variable arguments
axiom = EquivalentClasses(
    Class("http://example.org/A"),
    Class("http://example.org/B"),
    Class("http://example.org/C")
)
```

### py-horned-owl

```python
from pyhornedowl.model import EquivalentClasses

# List argument
a = ontology.clazz("http://example.org/A")
b = ontology.clazz("http://example.org/B")
c = ontology.clazz("http://example.org/C")
axiom = EquivalentClasses([a, b, c])
```

## Class Expressions

### funowl

```python
from funowl import (
    ObjectIntersectionOf, ObjectUnionOf, ObjectSomeValuesFrom,
    Class, ObjectProperty
)

# Intersection
expr = ObjectIntersectionOf(
    Class("http://example.org/A"),
    Class("http://example.org/B")
)

# Union
expr = ObjectUnionOf(
    Class("http://example.org/A"),
    Class("http://example.org/B")
)

# Existential restriction
expr = ObjectSomeValuesFrom(
    ObjectProperty("http://example.org/hasChild"),
    Class("http://example.org/Person")
)
```

### py-horned-owl

```python
from pyhornedowl.model import ObjectIntersectionOf, ObjectUnionOf, ObjectSomeValuesFrom

a = ontology.clazz("http://example.org/A")
b = ontology.clazz("http://example.org/B")
r = ontology.object_property("http://example.org/hasChild")
person = ontology.clazz("http://example.org/Person")

# Intersection - takes a list
expr = ObjectIntersectionOf([a, b])

# Union - takes a list
expr = ObjectUnionOf([a, b])

# Existential restriction
expr = ObjectSomeValuesFrom(r, person)

# Pythonic operators (py-horned-owl feature!)
expr = a & b           # ObjectIntersectionOf
expr = a | b           # ObjectUnionOf
expr = ~a              # ObjectComplementOf
expr = r.some(person)  # ObjectSomeValuesFrom
expr = r.only(person)  # ObjectAllValuesFrom
```

## Declarations

### funowl

```python
from funowl import Declaration, Class, ObjectProperty

ontology.axioms.append(Declaration(Class("http://example.org/MyClass")))
ontology.axioms.append(Declaration(ObjectProperty("http://example.org/myProp")))
```

### py-horned-owl

```python
from pyhornedowl.model import DeclareClass, DeclareObjectProperty

cls = ontology.clazz("http://example.org/MyClass")
prop = ontology.object_property("http://example.org/myProp")

ontology.add_axiom(DeclareClass(cls))
ontology.add_axiom(DeclareObjectProperty(prop))

# Or use convenience methods
ontology.declare_class("http://example.org/MyClass")
ontology.declare_object_property("http://example.org/myProp")
```

## Literals

### funowl

```python
from funowl import Literal

lit = Literal("Hello World")
lit = Literal(42)
lit = Literal("2024-01-01", "http://www.w3.org/2001/XMLSchema#date")
```

### py-horned-owl

```python
from pyhornedowl.model import SimpleLiteral, DatatypeLiteral, LanguageLiteral

# Plain literal
lit = SimpleLiteral("Hello World")

# Typed literal
lit = DatatypeLiteral("2024-01-01", ontology.iri("http://www.w3.org/2001/XMLSchema#date"))

# Language-tagged literal
lit = LanguageLiteral("Bonjour", "fr")
```

## Annotations and Axiom Annotations

### funowl

```python
from funowl import Annotation, AnnotationAssertion, SubClassOf

# Annotation assertion
axiom = AnnotationAssertion(
    "http://www.w3.org/2000/01/rdf-schema#label",
    "http://example.org/MyClass",
    Literal("My Class")
)
ontology.axioms.append(axiom)

# Axiom with annotations
subclass = SubClassOf(
    Class("http://example.org/A"),
    Class("http://example.org/B"),
    annotations=[Annotation("http://purl.org/dc/terms/source", Literal("Auto"))]
)
```

### py-horned-owl

```python
from pyhornedowl.model import (
    Annotation, AnnotationAssertion, AnnotationProperty,
    SubClassOf, SimpleLiteral, AnnotatedComponent
)

# Annotation assertion
rdfs_label = ontology.annotation_property("http://www.w3.org/2000/01/rdf-schema#label")
subject_iri = ontology.iri("http://example.org/MyClass")
ann = Annotation(rdfs_label, SimpleLiteral("My Class"))
axiom = AnnotationAssertion(subject_iri, ann)
ontology.add_axiom(axiom)

# Axiom with annotations
a = ontology.clazz("http://example.org/A")
b = ontology.clazz("http://example.org/B")
source_prop = ontology.annotation_property("http://purl.org/dc/terms/source")
annotation = Annotation(source_prop, SimpleLiteral("Auto"))

# Method 1: Add with annotations
axiom = SubClassOf(a, b)
ontology.add_axiom(axiom, {annotation})

# Method 2: Use AnnotatedComponent
axiom = SubClassOf(a, b)
annotated = AnnotatedComponent(axiom, {annotation})
# Then add using a helper function
```

## Serialization

### funowl

```python
# To OWL Functional Syntax string
owl_string = str(doc)

# To RDF
from rdflib import Graph
g = Graph()
doc.to_rdf(g)
turtle_string = g.serialize(format="turtle")
```

### py-horned-owl

```python
# To string (various formats)
ofn_string = ontology.save_to_string("ofn")   # OWL Functional
owl_string = ontology.save_to_string("owl")   # RDF/XML
owx_string = ontology.save_to_string("owx")   # OWL/XML

# To file
ontology.save_to_file("output.ofn", "ofn")
ontology.save_to_file("output.owl", "owl")
ontology.save_to_file("output.owx")  # Format inferred from extension
```

## Parsing

### funowl

```python
from funowl.converters.functional_converter import to_python

# Parse from string
doc = to_python(owl_functional_string)

# Parse from file
with open("ontology.ofn") as f:
    doc = to_python(f.read())

# Access axioms
for axiom in doc.ontology.axioms:
    print(axiom)
```

### py-horned-owl

```python
import pyhornedowl

# Parse from file
ontology = pyhornedowl.open_ontology("ontology.owl")  # RDF/XML
ontology = pyhornedowl.open_ontology("ontology.owx")  # OWL/XML

# Parse from string with explicit format
ontology = pyhornedowl.open_ontology_from_string(owl_string, "ofn")
ontology = pyhornedowl.open_ontology_from_string(owl_string, "owl")

# Access axioms (returns AnnotatedComponent list)
for annotated_axiom in ontology.get_axioms():
    axiom = annotated_axiom.component
    annotations = annotated_axiom.ann
    print(axiom)
```

## Retrieving Axioms and Classes

### funowl

```python
axioms = doc.ontology.axioms
# No built-in method to get all classes
```

### py-horned-owl

```python
# All axioms
axioms = ontology.get_axioms()  # Returns List[AnnotatedComponent]

# All classes (IRIs as strings)
classes = ontology.get_classes()  # Returns Set[str]

# All object properties
properties = ontology.get_object_properties()  # Returns Set[str]

# Axioms for a specific IRI
axioms_for_class = ontology.get_axioms_for_iri("http://example.org/MyClass")

# Get annotation value
label = ontology.get_annotation(
    "http://example.org/MyClass",
    "http://www.w3.org/2000/01/rdf-schema#label"
)
```

## Complete Example

### funowl

```python
from funowl import (
    OntologyDocument, Ontology, Prefix, Class, ObjectProperty,
    SubClassOf, EquivalentClasses, ObjectSomeValuesFrom,
    ObjectIntersectionOf, Declaration, Literal, AnnotationAssertion
)

# Create ontology
ontology = Ontology("http://example.org/pizza")
doc = OntologyDocument("http://example.org/pizza", ontology)
doc.prefixDeclarations.append(Prefix("pizza", "http://example.org/pizza#"))

# Declare classes
ontology.axioms.append(Declaration(Class("http://example.org/pizza#Pizza")))
ontology.axioms.append(Declaration(Class("http://example.org/pizza#Topping")))

# Add label
ontology.axioms.append(AnnotationAssertion(
    "http://www.w3.org/2000/01/rdf-schema#label",
    "http://example.org/pizza#Pizza",
    Literal("Pizza")
))

# Define MargheritaPizza
ontology.axioms.append(EquivalentClasses(
    Class("http://example.org/pizza#MargheritaPizza"),
    ObjectIntersectionOf(
        Class("http://example.org/pizza#Pizza"),
        ObjectSomeValuesFrom(
            ObjectProperty("http://example.org/pizza#hasTopping"),
            Class("http://example.org/pizza#TomatoTopping")
        )
    )
))

# Serialize
print(str(doc))
```

### py-horned-owl

```python
import pyhornedowl
from pyhornedowl.model import (
    SubClassOf, EquivalentClasses, ObjectSomeValuesFrom,
    ObjectIntersectionOf, DeclareClass, SimpleLiteral,
    Annotation, AnnotationAssertion
)

# Create ontology
ontology = pyhornedowl.PyIndexedOntology()
ontology.add_prefix_mapping("pizza", "http://example.org/pizza#")

# Create entities
pizza = ontology.clazz("http://example.org/pizza#Pizza")
topping = ontology.clazz("http://example.org/pizza#Topping")
margherita = ontology.clazz("http://example.org/pizza#MargheritaPizza")
tomato = ontology.clazz("http://example.org/pizza#TomatoTopping")
has_topping = ontology.object_property("http://example.org/pizza#hasTopping")
rdfs_label = ontology.annotation_property("http://www.w3.org/2000/01/rdf-schema#label")

# Declare classes
ontology.add_axiom(DeclareClass(pizza))
ontology.add_axiom(DeclareClass(topping))

# Add label
pizza_iri = ontology.iri("http://example.org/pizza#Pizza")
ontology.add_axiom(AnnotationAssertion(
    pizza_iri,
    Annotation(rdfs_label, SimpleLiteral("Pizza"))
))

# Define MargheritaPizza (using list syntax)
ontology.add_axiom(EquivalentClasses([
    margherita,
    ObjectIntersectionOf([
        pizza,
        ObjectSomeValuesFrom(has_topping, tomato)
    ])
]))

# Alternative using Pythonic operators
definition = pizza & has_topping.some(tomato)
ontology.add_axiom(EquivalentClasses([margherita, definition]))

# Serialize
print(ontology.save_to_string("ofn"))
```

## Tips for Migration

1. **Start with factory methods**: Always use `ontology.clazz()`, `ontology.object_property()`, etc. instead of direct model constructors for better IRI caching.

2. **Remember the list syntax**: N-ary axioms and class expressions like `EquivalentClasses`, `ObjectIntersectionOf`, and `ObjectUnionOf` take lists in py-horned-owl.

3. **Handle AnnotatedComponent**: When iterating axioms, remember that `get_axioms()` returns `AnnotatedComponent` wrappers. Access the actual axiom via `.component`.

4. **Use Pythonic operators**: py-horned-owl supports `&`, `|`, `~`, `.some()`, `.only()` for building class expressions.

5. **Check prefix mappings**: py-horned-owl's OFN parser is strict about prefix declarations. Ensure all prefixes are declared before parsing.

## Resources

- [py-horned-owl documentation](https://ontology-tools.github.io/py-horned-owl/)
- [py-horned-owl GitHub](https://github.com/ontology-tools/py-horned-owl)
- [PyPI package](https://pypi.org/project/py-horned-owl/)
- [horned-owl Rust library](https://github.com/phillord/horned-owl)
- [horned-owl paper](https://drops.dagstuhl.de/opus/volltexte/2023/18374/) - "Horned-OWL: Flying Further and Faster with Ontologies"
