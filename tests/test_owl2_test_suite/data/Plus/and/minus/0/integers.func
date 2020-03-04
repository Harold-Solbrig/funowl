Prefix(:=<http://example.org/>)
Prefix(xsd:=<http://www.w3.org/2001/XMLSchema#>)
Ontology(
  Declaration(NamedIndividual(:a))
  Declaration(DataProperty(:dp))
  Declaration(Class(:A))
  SubClassOf(:A DataAllValuesFrom(:dp 
    DataOneOf("0"^^xsd:integer))
  ) 
  ClassAssertion(:A :a)
  ClassAssertion(
    DataSomeValuesFrom(:dp DataOneOf("-0"^^xsd:integer)) :a
  )
)