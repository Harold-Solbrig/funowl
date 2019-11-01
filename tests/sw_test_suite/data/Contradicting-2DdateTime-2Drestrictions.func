Prefix(:=<http://example.org/>)
Prefix(xsd:=<http://www.w3.org/2001/XMLSchema#>)
Ontology(
  Declaration(NamedIndividual(:a))
  Declaration(DataProperty(:dp))
  Declaration(Class(:A))
  SubClassOf(:A 
    DataHasValue(:dp "2007-10-08T20:44:11.656+01:00"^^xsd:dateTime)) 
  SubClassOf(:A 
    DataAllValuesFrom(:dp DatatypeRestriction(
      xsd:dateTime 
      xsd:minInclusive "2008-07-08T20:44:11.656+01:00"^^xsd:dateTime 
      xsd:maxInclusive "2008-10-08T20:44:11.656+01:00"^^xsd:dateTime)
    )
  ) 
  ClassAssertion(:A :a)
)