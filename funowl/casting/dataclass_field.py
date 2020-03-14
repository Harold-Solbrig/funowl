import logging
from argparse import Namespace
from dataclasses import Field, MISSING, field, fields, dataclass
from typing import Type, List, Any, Union, ClassVar, Optional

from rdflib import URIRef, Graph, XSD, RDF, RDFS, OWL

from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.general_definitions import AbbreviatedIRI, FullIRI
from funowl.writers.FunctionalWriter import FunctionalWriter


def exclude(exclusions: List[Type], *, default=MISSING, coercion_allowed: bool = True) -> Field:
    return field(default=default, metadata={"exclude":exclusions, "coercin_allowed": coercion_allowed})


def cast(typ: Type, v: Any) -> Any:
    """
    Convert value v to type typ.  Raises TypeError if conversion is not possible.  Note that None and empty lists are
    treated as universal types

    :param typ: target type to convert v to
    :param v: value to convert to type
    :param _coercion_allowed: True means type coercion is allowed.  False means only matching types work
    :return: instance of type
    """
    poss_types = fields(typ)
    print("HERE")
    #
    # def choice_match(poss_type: Callable[[Type], Any]) -> Any:
    #     logging.debug(f"     Matches {poss_type.__name__}")
    #     if getattr(poss_type, '_parse_input', None):
    #         rval = typ(poss_type(*poss_type._parse_input(v)))
    #     else:
    #         rval = typ(poss_type(v))
    #     rval.from_cast = True
    #     return rval

    # if v is None or v == []:  # Null and empty list are always allowed (a bit too permissive but...)
    #     return v
    #
    # # Union[...]
    # if is_union(typ):
    #     for t in get_args(typ):
    #         if type(v) is t:
    #             return v
    #     for t in get_args(typ):
    #         if _coercion_allowed is not False and isinstance_(v, t):
    #             return cast(t, v)
    #     raise TypeError(f"Type mismatch between {v} (type: {type(v)} and {typ}")
    #
    # # List[...]
    # if is_iterable(typ):
    #     list_type = get_args(typ)[0]
    #     if isinstance(v, str) or not isinstance(v, Iterable):  # You can assign a singleton directly
    #         v = [v]
    #     return [cast(list_type, vi) for vi in v]
    #
    # if issubclass(type(v), typ):        # conversion is treated as idempotent (typ(typ(v)) = typ(v)
    #     return copy(v)
    #
    # if isinstance(typ, type) and issubclass(typ, FunOwlChoice):
    #     hints = typ.hints()
    #     if logging.getLogger().level <= logging.DEBUG:
    #         pos_types = ', '.join([t.__name__ for t in hints])
    #         logging.debug(f"value: {v} (type: {type(v)}) testing against {typ}[{pos_types}]")
    #     for poss_type in hints:
    #         if issubclass(type(v), poss_type):
    #             return choice_match(poss_type)
    #     for poss_type in hints:
    #         if issubclass(type(v), poss_type) or (_coercion_allowed is not False and isinstance(v, poss_type)):
    #             return choice_match(poss_type)
    #     logging.debug('     No match')
    #
    # # Determine whether v can be cooreced into type
    # if _coercion_allowed is False or not isinstance_(v, typ):
    #     raise TypeError(f"value: {v} (type: {type(v)}) cannot be converted to {typ}")
    #
    # # Vanilla typing
    # return typ(*(getattr(typ, '_parse_input', lambda e: e))(v))


@dataclass(unsafe_hash=True)
class IRI(FunOwlChoice):
    """ IRI := fullIRI | abbreviatedIRI """
    v: Union[AbbreviatedIRI, FullIRI, URIRef, str] = exclude([URIRef, str])
    rdf_type: ClassVar[URIRef] = None
    _input_types: ClassVar[Type] = [URIRef, str]
    from_cast: bool = False

    def full_uri(self, g: Graph) -> Optional[URIRef]:
        if isinstance(self.v, URIRef):
            return self.v
        if isinstance(self.v, AbbreviatedIRI):
            # TODO: find the code in rdflib that does this
            ns, local = self.v.split(':', 1)
            for ns1, uri in g.namespaces():
                if ns == ns1:
                    return(Namespace(uri)[local])
            logging.warning(f"IRI: {self.v} - {ns} not a valid prefix")
            return None
        if isinstance(self.v, FullIRI):
            return URIRef(self.v)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        fulluri = self.full_uri(w.g)
        return w + (fulluri.n3(w.g.namespace_manager) if fulluri else self.v)

    def to_rdf(self, g: Graph) -> URIRef:
        fulluri = self.full_uri(g)
        if self.rdf_type:
            # Filter: for (undocumented?) reasons, never assert owl:thing a owl:Class
            if not (fulluri.startswith(str(XSD)) or
                    fulluri.startswith(str(RDF)) or
                    fulluri.startswith(str(RDFS)) or
                    fulluri.startswith(str(OWL))
            ) or not self.from_cast:
                g.add((fulluri, RDF.type, self.rdf_type))

        return fulluri


t = IRI("http://foo.org/")

for f in fields(IRI):
    if f.name == 'v':
        print("HERE")
        # t = list(get_args(hints)) if is_union(hints) else [hints]
        # return [e for e in t if e not in cls._input_types] if cls._input_types else t