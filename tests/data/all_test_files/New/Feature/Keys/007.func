Prefix( : = <http://example.org/> )

Ontology(
  Declaration( Class( :Person ) )
  Declaration( Class( :Man ) )
  Declaration( DataProperty( :hasSSN ) )
  Declaration( ObjectProperty( :marriedTo ) )

  HasKey( :Person () ( :hasSSN ) )

  DataPropertyAssertion( :hasSSN :Peter "123-45-6789" )
  ClassAssertion( :Person :Peter )

  ClassAssertion(
    ObjectSomeValuesFrom(
       :marriedTo
       ObjectIntersectionOf( :Man DataHasValue( :hasSSN "123-45-6789" ) )
    )
    :Lois
  )

  SubClassOf( :Man :Person )
)