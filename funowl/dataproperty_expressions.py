from dataclasses import dataclass

from rdflib import OWL

from funowl.identifiers import IRI


@dataclass
class DataProperty(IRI):
    rdf_type = OWL.DatatypeProperty


# DataPropertyExpression is just a synonym for dataproperty
@dataclass
class DataPropertyExpression(DataProperty):
    pass
