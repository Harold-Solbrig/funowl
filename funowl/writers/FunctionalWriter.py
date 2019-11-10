from typing import List, Optional, Callable, Union, Any

from rdflib import Graph, OWL, URIRef


class FunctionalWriter:
    DEFAULT_TAB: str = '    '

    def __init__(self, tab: Optional[str] = None, g: Optional[Graph] = None) -> None:
        """ Create a FunctionalWriter instance

        :param tab: what to emit for a tab setting.  Default: DEFAULT_TAB
        :param g: graph to use for IRI resolution.  Default - default rdflib graph
        """
        self.tab = FunctionalWriter.DEFAULT_TAB if tab is None else tab
        if g is None:
            self.g = Graph()
            self.g.bind('owl', OWL)
        else:
            self.g = g
        self._indent = 0
        self.output: List[str] = []
        self._line = ''
        self._inside_function = False
        self.reset()            # Not strictly needed - we put the initializers above for lint purposes

    def reset(self) -> "FunctionalWriter":
        """ Reset the writer contents
        :return: FunctionWriter instance
        """
        self._indent = 0
        self.output: List[str] = []
        self._line = ''
        self._inside_function = False
        return self

    def bind(self, localname: str, namespace: Union[str, URIRef]) -> "FunctionalWriter":
        """
        Add a namespace.
        :param localname: namespace
        :param namespace: UIRI
        :return: FunctionalWriter instance
        """
        self.g.bind(localname, namespace)

    def __add__(self, other: Any) -> "FunctionalWriter":
        """
         Add other to the current line
        :param other: string or stringifiable object to add
        :return: FunctionWriter instance
        """
        return self.concat(other, sep=' ')

    def concat(self, *eles: Any, sep: str = '') -> "FunctionalWriter":
        """ Add the list of positional arguments to the output, separated by sep
        :param eles: Positional arguments to add
        :param sep: Output separator
        :return: FunctionWriter instance
        """
        for el in eles:
            if hasattr(el, 'to_functional') and callable(getattr(el, 'to_functional')):
                w = FunctionalWriter(g=self.g)
                w._inside_function = self._inside_function
                line = str(el.to_functional(w))
            elif isinstance(el, FunctionalWriter):
                raise ValueError("FunctionalWriter can never be concatenated to itself")
            else:
                line = str(el)
            self._line += (sep if not self.bol() else '') + line
        return self

    def bol(self) -> bool:
        """ Return True if at the beginning of a line and NOT the beginning of a "document" """
        return not bool(self._line.strip())

    def getvalue(self) -> str:
        """
        Return the current writer content
        """
        return '\n'.join(self.contents).rstrip()

    @property
    def contents(self) -> List[str]:
        return self.output + [self._line if not self.bol() else '']

    def add(self, line: Any = None) -> "FunctionalWriter":
        """
         Add a line to the output
        :param line: String or to add to the output
        :return: FunctionWriter instance
        """
        if line is not None:
            self.concat(line, sep='')
        return self.br()

    def append(self, lines: List[Any]) -> "FunctionalWriter":
        """ Add a list of lines to the output, indenting appropriately
        :return: FunctionWriter instance
        """
        for line in lines:
            self.br().add(line)
        return self.br()

    def br(self, cond: bool = True) -> "FunctionalWriter":
        """ Output a line break if not at the beginning of the line and then indent
        :param cond: If false, act as a no-op
        :return: FunctionWriter instance
        """
        if cond:
            if not self.bol():
                self.output.append(self._line.rstrip())
            self._line = self.tab * self._indent
        return self

    def hardbr(self) -> "FunctionalWriter":
        """ Output a line break and then indent
        :return: FunctionWriter instance
        """
        if not self.bol():
            self.br()
        else:
            self.output.append('')
        return self

    def indent(self, line: Optional[Any] = None) -> "FunctionalWriter":
        """ Flush the buffer and increase the indent level
        :return: FunctionWriter instance
        """
        self._indent += 1
        return self.br().add(line)

    def outdent(self, line: Optional[Any] = None) -> "FunctionalWriter":
        """ Flush the buffer and decrease the indent level
        :return: FunctionWriter instance
        """
        self._indent = max(self._indent - 1, 0)
        return self.br().add(line)

    def func(self, func_name: Union[str, Any], contents: Optional[Callable[[], "FunctionalWriter"]] = None,
             indent: bool = True) -> "FunctionalWriter":
        """
        Generate a functional method in the form of "func( ... )"
        
        :param func_name: Function name or object.  If object, the class name is used
        :param contents: Invoked to generate function contents
        :param indent: Put interior on the same line if False
        :return: FunctionWriter instance
        """
        if not isinstance(func_name, str):
            func_name = type(func_name).__name__
        inside = self._inside_function
        self._inside_function = True
        (self.indent() if inside and indent else self) + (func_name + '(')
        contents() if contents else None
        self + ')'
        self._inside_function = inside
        return self.outdent() if inside and indent else self

    def iter(self, *objs: List[Any], f: Optional[Callable[[Any], "FunctionalWriter"]] = None, indent: bool=True) \
            -> "FunctionalWriter":
        """
         Iterate over a list of lists of FunOwlRoot objects, emitting the the values if they are not emtpy
        :param objs: Positional list of lists of FunOwlRoot objects
        :param f: Function to invoke to emit each object
        :param indent: True means indent one level
        :return: FunctionWriter instance
        """

        # Empty lists emit nothing
        if all(not obj for obj in objs):
            return self

        if indent:
            self.br().indent()
        for objlist in objs:
            if objlist:
                for obj in objlist:
                    f(obj) if f is not None else (self + obj).br()
        if indent:
            self.outdent()
        return self

    def opt(self, v: Optional[Any], sep: str = ' ') -> "FunctionalWriter":
        """ Emit v if it exists 
        :param v: Optional item to emit
        :param sep: separator
        :return: FunctionWriter instance
        """
        return self if v is None else self.concat(v, sep=sep)

    def __repr__(self):
        return '"' + self.getvalue() + '"'

    def __str__(self):
        return self.getvalue()
