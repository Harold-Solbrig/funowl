import logging
from collections import Iterable
from copy import copy
from typing import Type, Any, Optional, get_type_hints

from funowl.terminals.TypingHelper import is_union, get_args, is_iterable, isinstance_


def cast(typ: Type, v: Any, _coercion_allowed: Optional[bool] = None) -> Any:
    """
    Convert value v to type typ.  Raises TypeError if conversion is not possible.  Note that None and empty lists are
    treated as universal types

    :param typ: type to convert v to
    :param v: value to convert to type
    :param _coercion_allowed: True means type coercion is allowed.  False means only matching types work
    :return: instance of type
    """
    from funowl.base.fun_owl_choice import FunOwlChoice

    if v is None or v == []:  # Null and empty list are always allowed (a bit too permissive but...)
        return v

    # Union[...]
    if is_union(typ):
        for t in get_args(typ):
            if type(v) is t:
                return v
            elif _coercion_allowed is not False and isinstance_(v, t):
                return cast(t, v)
        raise TypeError(f"Type mismatch between {v} (type: {type(v)} and {typ}")

    # List[...]
    if is_iterable(typ):
        list_type = get_args(typ)[0]
        if isinstance(v, str) or not isinstance(v, Iterable):  # You can assign a singleton directly
            v = [v]
        return [cast(list_type, vi) for vi in v]

    if issubclass(type(v), typ):        # conversion is treated as idempotent (typ(typ(v)) = typ(v)
        return copy(v)

    if isinstance(typ, type) and issubclass(typ, FunOwlChoice):
        hints = typ.hints()
        pos_types = ', '.join([t.__name__ for t in hints])
        logging.debug(f"value: {v} (type: {type(v)}) testing against {typ}[{pos_types}]")
        for poss_type in hints:
            if issubclass(type(v), poss_type) or (_coercion_allowed is not False and isinstance(v, poss_type)):
                logging.debug(f"     Matches {poss_type.__name__}")
                if getattr(poss_type, '_parse_input', None):
                    return typ(poss_type(*poss_type._parse_input(v)))
                return typ(poss_type(v))
        logging.debug('     No match')

    # Determine whether v can be cooreced into type
    if _coercion_allowed is False or not isinstance_(v, typ):
        raise TypeError(f"value: {v} (type: {type(v)}) cannot be converted to {typ}")

    # Vanilla typing
    return typ(*(getattr(typ, '_parse_input', lambda e: e))(v))
