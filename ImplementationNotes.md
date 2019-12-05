# Implementation Notes
This project is based on the following:
* [OWL 2 Web Ontology Language Structural Specification and Functional-Style Syntax (Second Edition)](https://www.w3.org/TR/owl2-syntax/)

## Functions that take open ended lists as arguments
When a function takes a list of arguments such as `ObjectUnionOf`:

```
ObjectUnionOf := 'ObjectUnionOf' '(' ClassExpression ClassExpression { ClassExpression } ')' 
```

which says that `ObjectUnionOf` can have 2 or more `ClassExpressions`, the literal mapping of this to the `funowl` 
Python idiom would be:

```python

@dataclass
class ObjectUnionOf(FunOwlBase):
    classExpressions: List["ClassExpression"]

    ...
```

This turns out to be a less than optimal in the python idiom, as `ObjectUnionOf( a:Man a:Woman )` would have to
 be constructed using a list:

```python
u = ObjectUnionOf([A.Man, A.Woman])
```

In this case, we override the constructor:
```python

@dataclass
class ObjectUnionOf(FunOwlBase):
    classExpressions: List["ClassExpression"]

    def __init__(self, *classExpression: "ClassExpression") -> None:
        self.classExpressions = list(classExpression)
        super().__init__()
```

Resulting in the more natural:
```python
u = ObjectUnionOf(A.Man, A.Woman)
```