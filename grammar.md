
| production | definition | Type  | Module | Class |
| ---------- | ---------- | ----- | ------ | ----- | 
| LANGTAG    | r'[a-zA-Z]+(\-([a-zA-Z0-9])+)*' | Terminal | Terminals | LANGTAG |
| HEX | r'[0-9]/[A-F]/[a-f]' | Terminal | Terminals | HEX |
| UCHAR | r'\\\\u({HEX})({HEX})({HEX})({HEX})/\\\\U({HEX})({HEX})({HEX})({HEX})({HEX})({HEX})({HEX})({HEX})'|  Terminal 
| IRIREF | r'([^\u0000-\u0020\u005C\u007B\u007D<>"/^`]/({UCHAR}))*'|  Terminal | Terminals | IRIREF|
|  PN_CHARS_BASE | r'[A-Z]/[a-z]/[\u00C0-\u00D6]/[\u00D8-\u00F6]/[\u00F8-\u02FF]/[\u0370-\u037D]/[\u037F-\u1FFF]/[\u200C-\u200D]/[\u2070-\u218F]/[\u2C00-\u2FEF]/[\u3001-\uD7FF]/[\uF900-\uFDCF]/[\uFDF0-\uFFFD]/[\U00010000-\U000EFFFF]') | Terminal | Terminals |   PN_CHARS_BASE |
|  PN_CHARS_U | r'({PN_CHARS_BASE})/_' | Terminal | Terminals |   PN_CHARS_U |
|  PN_CHARS | r'({PN_CHARS_U})/\-/[0-9]/\\u00B7/[\u0300-\u036F]/[\u203F-\u2040]' | Terminal | Terminals |   PN_CHARS |
|  PNAME_NS | r'({PN_CHARS_BASE})((({PN_CHARS})/\.)*({PN_CHARS}))?' | Terminal | Terminals |   PNAME_NS |
|  PNAME_LOCAL | r'(({PN_CHARS_U})/[0-9])((({PN_CHARS})/\.)*({PN_CHARS}))?' | Terminal | Terminals |   PNAME_LOCAL |
|  BLANK_NODE_LABEL | r'_:(({PN_CHARS_U})/[0-9])((({PN_CHARS})/\.)*({PN_CHARS}))?' | Terminal | Terminals |   BLANK_NODE_LABEL |
|  PNAME_LN | r'({PNAME_NS})?:{PNAME_LOCAL}' | Terminal | Terminals |   PNAME_LN |
<hr/>

| production | definition | Type  | Module | Class |
| ---------- | ---------- | ----- | ------ | ----- | 
| nonNegativeInteger | a nonempty finite sequence of digits between 0 and 9 | Lexical | GeneralDefinitions | NonNegativeInteger |
| quotedString | a finite sequence of characters in which " (U+22) and \ (U+5C) occur only in pairs of the form \" (U+5C, U+22) and \\ (U+5C, U+5C), enclosed in a pair of " (U+22) characters | Lexical | GeneralDefinitions | QuotedString
| languageTag | @ (U+40) followed a nonempty sequence of characters matching the langtag production from [BCP 47] | Lexical | GeneralDefinitions | LanguageTag |
| nodeID | a finite sequence of characters matching the BLANK_NODE_LABEL production of [SPARQL] | Lexical | GeneralDefinitions | NodeId |
<hr/>

| production | definition | Type  | Module | Class |
| ---------- | ---------- | ----- | ------ | ----- | 
| fullIRI | an IRI as defined in [RFC3987], enclosed in a pair of < (U+3C) and > (U+3E) characters | Lexical | GeneralDefinitions | FullIRI |
| prefixName | a finite sequence of characters matching the as PNAME_NS production of [SPARQL] | Lexical | GeneralDefinitions | PrefixName |
| abbreviatedIRI | a finite sequence of characters matching the PNAME_LN production of [SPARQL] | Lexical | GeneralDefinitions | AbbreviatedIRI |
| IRI | fullIRI / abbreviatedIRI | FunOwlChoice | Identifiers

<hr/>

| production | definition | Type  | Module | Class |
| ---------- | ---------- | ----- | ------ | ----- | 
| ontologyDocument | { prefixDeclaration } OntologyDocument |  |
| prefixDeclaration | 'Prefix' '(' prefixName '=' fullIRI ')' | FunOwlBase | OntologyDocument | PrefixDeclaration |
| Ontology | 'Ontology' '(' [ ontologyIRI [ versionIRI ] ] directlyImportsDocuments ontologyAnnotations axioms ')' | Annotatable | OntologyDocument | Ontology|
| ontologyIRI | IRI | Optional[IRI] | OntologyDocument | iri: Optional[IRI] |
| versionIRI | IRI | Optional[IRI]  | OntologyDocument | version: Optional[IRI] |
| directlyImportsDocuments | { 'Import' '(' IRI ')' } | List[IMPORT] | OntologyDocument | Import |
| ontologyAnnotations | { Annotation } | List[Annotation] | Annotations | Annotation |
| axioms | { Axiom } | List[Axiom] | OntologyDocument | Axiom |
<hr/>

| production | definition | Type  | Module | Class |
| ---------- | ---------- | ----- | ------ | ----- | 
| Declaration | 'Declaration' '(' axiomAnnotations Entity ')' | Axiom, FunOwlChoice | Declarations | Declaration |