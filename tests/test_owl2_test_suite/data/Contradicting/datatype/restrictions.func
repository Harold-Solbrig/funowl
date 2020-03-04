Prefix(:=<http://example.org/>)
Prefix(xsd:=<http://www.w3.org/2001/XMLSchema#>)
Ontology(
  Declaration(NamedIndividual(:a))
  Declaration(DataProperty(:dp))
  Declaration(Class(:A))
  SubClassOf(:A DataAllValuesFrom(:dp 
    DataOneOf("3"^^xsd:integer "4"^^xsd:integer))
  ) 
  SubClassOf(:A DataAllValuesFrom(:dp 
    DataOneOf("2"^^xsd:integer "3"^^xsd:integer))
  )
  SubClassOf(:A DataSomeValuesFrom(:dp 
    DatatypeRestriction(xsd:integer 
      xsd:minInclusive "4"^^xsd:integer)
    )
  )
  ClassAssertion(:A :a)
)