import logging
from collections import Iterable, UserList
from copy import copy
from dataclasses import Field, MISSING, field
from typing import Type, Any, Optional, Union, List, TypeVar


from funowl.terminals.TypingHelper import is_union, get_args, isinstance_, is_list, is_dict, is_tuple, \
    is_set


# The basic problem we face is that when you are using an IDE, we want to be permissive.  As an example, if you are
# constructing an IRI, you can pass a fullIRI or an abbreviatedIRI, but you also want to accept an rdflib URIRef or
# any string that conforms to fullIRI or abbreviatedIRI syntax.
#
# If it is the latter two types, however (URIRef or str), we do NOT want to accept them if they don't conform.  The
# exclude function adds "exclude" metadata to the type hint that prevents coercion to the input only types.
def exclude(exclusions: List[Type], *, default=MISSING) -> Field:
    """
    :param exclusions: List of exclusions
    :param default: default value
    :return: Field definition
    """
    return field(default=default, metadata={"exclude": exclusions})


def remove_exclusions(typ: Union[Field, Type]) -> Union[List[Type], Type]:
    """
    Convert typ into an ordered list of possible types, removing any exclusions

    :param typ: Field, FunOwlChoice instance or Type definition
    :return: Ordered list of types with exclusions removed
    """
    from funowl.base.fun_owl_choice import FunOwlChoice

    if isinstance(typ, type) and issubclass(typ, FunOwlChoice):
        return typ.real_types()

    if isinstance_(typ, Field):
        # If it is a field, the actual type is Field.type.
        if is_union(typ.type):
            exclusions = typ.metadata.get('exclude', [])
            return [t for t in get_args(typ.type) if t not in exclusions]
        else:
            typ = typ.type
    return [typ]


def cast(cast_to: Union[Type, Field], v: Any, _coercion_allowed: Optional[bool] = None) -> Any:
    """
    Convert value v to type cast_to.  Raises TypeError if conversion is not possible.  Note that None and empty lists are
    treated as universal types

    :param cast_to: Field, FunOwlChoice instance or Type definition we want to cast v to
    :param v: value to cast.  Note that None and empty lists are treated as always cast.
    :param _coercion_allowed: True means type coercion is allowed.  False means only matching types work
    :return: instance of cast_to
    """
    from funowl.base.fun_owl_choice import FunOwlChoice

    def cast_to_choice(choice: FunOwlChoice, v: Any) -> Any:
        """ Process a choice """
        hints = choice.real_types()
        for poss_type in hints:
            if issubclass(type(v), poss_type):
                return choice_match(poss_type)
        for poss_type in hints:
            if issubclass(type(v), poss_type) or (_coercion_allowed is not False and isinstance(v, poss_type)):
                return choice_match(poss_type)
        logging.debug('     No match')

    def choice_match(matched_type: Type) -> Any:
        if hasattr(matched_type, '_parse_input'):
            rval = typ(matched_type(*matched_type._parse_input(v)))
        else:
            rval = typ(matched_type(v))
        return rval

    # TODO: this should be a parameterized type for return
    def do_cast(target_type: Type, target_value: Any) -> Any:
        return target_type(*(getattr(target_type, '_parse_input', lambda e: e))(target_value))

    # None and empty lists are universal types.  If already cast, we're done
    if v is None or v == [] or (isinstance_(cast_to, Field) and type(v) is cast_to.type) or type(v) is cast_to:
        return v

    # Create an ordered list of target types -- these are the types IN cast_to
    type_list = remove_exclusions(cast_to)

    # If we already match the list, no coercion is necessary
    for typ in type_list:
        if type(v) is typ:
            return v

    # Iterate through the list to determine whether we can coerce v to any of the targets
    if _coercion_allowed is not False:
        for typ in type_list:
            # Note: This parallels the code in TypingHelper.isinstance_  -- it may be worth considering merging these
            # with a visitor idiom

            # Any / unrealized TypeVar is the identity function
            # TODO: not all TypeVar situations will work here
            if typ is Any or isinstance(typ, TypeVar):
                return do_cast(typ, v)

            elif isinstance_(typ, FunOwlChoice):
                return cast_to_choice(typ, v)

            elif is_union(typ):
                for t in get_args(typ):
                    if isinstance_(v, t):
                        if type(v) is t:
                            return v
                        else:
                            return do_cast(t, v)

            elif is_dict(typ):
                if isinstance(v, dict):
                    dict_args = get_args(typ)
                    return {cast(dict_args[0], dk): cast(dict_args[1], dv) for dk, dv in v.items()} if dict_args else v

            elif is_list(typ):
                # casting x == [x]
                if isinstance(v, str) or not isinstance(v, Iterable):
                    v = [v]
                if isinstance(v, list) or isinstance(v, UserList):
                    list_type = get_args(typ)
                    return [cast(list_type[0], vi) for vi in v] if list_type else v

            elif is_tuple(typ):
                if isinstance(v, tuple):
                    tuple_args = get_args(typ)
                    return tuple(cast(tt, vt) for tt, vt in zip(tuple_args, v)) if tuple_args else v

            elif is_set(typ):
                if isinstance_(v, set):
                    set_type = get_args(typ)
                    return set(cast(set_type[0], e) for e in v) if set_type else v

            elif isinstance_(v, typ):
                return do_cast(typ, v if issubclass(typ, str) else copy(v))

    raise TypeError(f"Type mismatch between {v} (type: {type(v)} and {type_list}")
