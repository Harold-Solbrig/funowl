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
    DataOneOf("2"^^xsd:short "3"^^xsd:integer))
  )
  ClassAssertion(:A :a)
  ClassAssertion(DataSomeValuesFrom(:dp
    DataComplementOf(DataOneOf("3"^^xsd:integer))) :a
  )
)