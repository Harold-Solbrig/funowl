Prefix(:=<http://example.org/>)
Prefix(xsd:=<http://www.w3.org/2001/XMLSchema#>)
Ontology(
  Declaration(NamedIndividual(:a))
  Declaration(DataProperty(:dp))
  Declaration(Class(:A))
  SubClassOf(:A DataSomeValuesFrom(:dp 
    DatatypeRestriction(xsd:integer xsd:minInclusive "18"^^xsd:integer))
  ) 
  SubClassOf(:A DataAllValuesFrom(:dp 
    DatatypeRestriction(xsd:integer xsd:maxInclusive "10"^^xsd:integer))
  )
  ClassAssertion(:A :a)
)