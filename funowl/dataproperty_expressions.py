from dataclasses import dataclass

from rdflib import OWL

from funowl.identifiers import IRI


@dataclass
class DataProperty(IRI):
    rdf_type = OWL.DatatypeProperty


# DataPropertyExpression is just a synonym for DataProperty
# Note: Lint error below is an IDE problem, not a real problem
@dataclass
class DataPropertyExpression(DataProperty):
    rdf_type = OWL.DatatypeProperty
