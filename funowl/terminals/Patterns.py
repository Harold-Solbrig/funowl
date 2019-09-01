import re
from abc import abstractmethod
from typing import Optional, Any, Union, Tuple

from funowl.terminals.TypingHelper import isinstance_


class Validateable:
    """
    Mixin -- any class with an _is_valid function
    """
    @abstractmethod
    def _is_valid(self) -> bool:
        """ Determine whether the element is valid

        :return: True if valid, false otherwise
        """
        raise NotImplementedError("_is_valid must be implemented")

    @property
    def _class_name(self) -> str:
        return type(self).__name__


class Pattern:
    """
    A lexerRuleBlock
    """
    def __init__(self, pattern: str):
        """
        Compile and record a match pattern

        :param pattern: regular expression
        """
        self.pattern_re = re.compile(pattern, flags=re.DOTALL)

    def __str__(self):
        return self.pattern_re.pattern

    def matches(self, txt: str) -> bool:
        """Determine whether txt matches pattern

        :param txt: text to check
        :return: True if match
        """
        # rval = ref.getText()[1:-1].encode('utf-8').decode('unicode-escape')
        if r'\\u' in self.pattern_re.pattern:
            txt = txt.encode('utf-8').decode('unicode-escape')
        match = self.pattern_re.match(txt)
        return match is not None and match.end() == len(txt)


class PatternedValMeta(type):
    pattern: Optional[Pattern]
    python_type: None

    def __instancecheck__(self, instance) -> bool:
        return instance is not None and \
               isinstance_(instance, self.python_type) and (self.pattern is None or self.pattern.matches(str(instance)))


class Patterned(Validateable, metaclass=PatternedValMeta):
    pattern: Optional[Pattern] = None

    def __init__(self, val: Any) -> None:
        if not isinstance(val, type(self)):
            raise ValueError(f'Invalid {self._class_name} value: "{val}"')

    def _is_valid(self) -> bool:
        return True

    @property
    def val(self) -> Any:
        return self


class String(str, Patterned):
    """
    A lexerRuleSpec implementation
    """
    pattern: Optional[Pattern] = None
    python_type = str


class Number(float, Patterned):
    """ Implementation of JSG @number type """
    pattern = Pattern(r'-?(0|[1-9][0-9]*)(.[0-9]+)?([eE][+-]?[0-9]+)?')
    python_type = (int, float, str)

    @property
    def val(self) -> Union[int, float]:
        return int(self) if Integer.pattern.matches(str(self)) else self


class Integer(int, Patterned):
    """ Implementation of JSG @int type """
    pattern = Pattern(r'-?(0|[1-9][0-9]*)')
    python_type = (int, str)

    def __new__(cls, v):
        if isinstance(v, bool) or not isinstance(v, Integer):
            raise ValueError(f"Invalid {cls.__name__} value: {v}")
        return super().__new__(cls, v)


class Boolean(Validateable, metaclass=PatternedValMeta):
    true_pattern = Pattern(r'[Tt]rue')
    false_pattern = Pattern(r'[Ff]alse')
    pattern = Pattern(r'{}|{}'.format(true_pattern, false_pattern))
    python_type = (int, str)

    def __new__(cls, v) -> bool:
        if not isinstance(v, cls):
            raise ValueError(f"Invalid {cls.__name__} value: {v}")

        return v if isinstance(v, bool) else cls.true_pattern.matches(str(v))

    def _is_valid(self) -> bool:
        return True
