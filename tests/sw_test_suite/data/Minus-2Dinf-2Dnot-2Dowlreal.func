Prefix(:=<http://example.org/>)
Prefix(xsd:=<http://www.w3.org/2001/XMLSchema#>)
Prefix(owl:=<http://www.w3.org/2002/07/owl#>)
Ontology(
  Declaration(NamedIndividual(:a))
  Declaration(DataProperty(:dp))
  Declaration(Class(:A))
  SubClassOf(:A DataAllValuesFrom(:dp owl:real)) 
  SubClassOf(:A 
    DataSomeValuesFrom(:dp DataOneOf("-INF"^^xsd:float "-0"^^xsd:integer))
  )
  ClassAssertion(:A :a) 
  NegativeDataPropertyAssertion(:dp :a "0"^^xsd:unsignedInt)
)