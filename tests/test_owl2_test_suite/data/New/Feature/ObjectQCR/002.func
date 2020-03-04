Prefix( : = <http://example.org/> )

Ontology(
  Declaration( ObjectProperty( :fatherOf ) )
  Declaration( Class( :Woman ) )

  ObjectPropertyAssertion( :fatherOf :Peter :Stewie )
  ObjectPropertyAssertion( :fatherOf :Peter :Meg )

  ClassAssertion( :Woman :Meg )
  ClassAssertion( ObjectMaxCardinality( 1 :fatherOf :Woman ) :Peter )

  DifferentIndividuals( :Stewie :Meg )
)