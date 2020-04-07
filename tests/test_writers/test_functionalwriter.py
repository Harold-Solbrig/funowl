import unittest
from dataclasses import dataclass

from rdflib import Namespace

from funowl.base.fun_owl_base import FunOwlRoot, FunOwlBase
from funowl.writers.FunctionalWriter import FunctionalWriter
from funowl.identifiers import IRI
from tests.utils.base import TestBase

EX = Namespace("http://example.org/ex/")


class FunctionalWriterTestCase(TestBase):
    def test_writer(self):
        self.w.add("Foo(").indent('A').indent('B')
        self.w.add('C').outdent('D').outdent(')')
        self.assertEqual("""Foo(
    A
        B
        C
    D
)""", self.w.getvalue())

    def test_append(self):
        self.w.add("Foo(").indent('B').append(['C', 'D', 'E']).outdent(')')
        self.assertEqual("""Foo(
    B
    C
    D
    E
)""", self.w.getvalue())

    def test_add(self):
        self.w.add("Foo(").indent()
        self.w + 'rdf:type'
        self.w + 'foaf:Person'
        self.w.outdent(')')
        self.assertEqual("Foo(\n    rdf:type foaf:Person\n)", self.w.getvalue())

    def test_hardbr(self):
        self.w.add("Foo(").indent()
        self.w + 'rdf:type'
        self.w.hardbr()
        self.w.hardbr()
        self.w + 'foaf:Person'
        self.w.outdent(')')
        self.assertEqual("Foo(\n    rdf:type\n\n    foaf:Person\n)", self.w.getvalue())

    def test_function(self):
        self.assertEqual("""Foo(
    Bar( HERE There )
)""", self.w.func("Foo", lambda: self.w.func("Bar", lambda: self.w + "HERE" + "There")).getvalue())

    def test_function_class(self):
        class Phedra:
            pass
        self.assertEqual('Phedra( phoo )', self.w.func(Phedra(), lambda: self.w + 'phoo').getvalue())

    def test_join_functional_outputs(self):
        @dataclass
        class T1(FunOwlRoot):
            v: IRI

            def __init__(self, v: str) -> None:
                self.v = EX[v]

            def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
                return w + self.v

        wt = FunctionalWriter()
        wt.bind('ex', EX)
        wt + "The values are:"
        T1("I1").to_functional(wt)
        T1("I2").to_functional(wt)
        T1("I3").to_functional(wt)
        self.assertEqual("The values are: ex:I1 ex:I2 ex:I3", wt.getvalue())

    def test_func_name(self):
        class Foo(FunOwlBase):
            pass
        f = Foo()
        self.assertEqual("Foo( )", str(self.w.func(f, lambda: self.w)))
        self.w.reset()
        self.assertEqual('"Foo( a b c )"', repr(self.w.func(f, lambda: self.w + 'a b c')))
        self.w.reset()
        self.assertEqual("Foo(\n    a b c\n)", str(self.w.func(f, lambda: self.w.indent('a b c').outdent())))
        self.w.reset()
        self.assertEqual("    Foo(\n        a b c\n    )",
                         str(self.w.indent().func(f, lambda: self.w.indent('a b c').outdent())))

    def test_opt(self):
        class Foo(FunOwlBase):
            def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
                return w.func(self, lambda: w)

        self.assertEqual('', str(self.w.opt(None)))
        self.w.reset()
        self.assertEqual('17', str(self.w.opt(17)))
        self.w.reset()
        self.assertEqual('Foo( )', str(self.w.opt(Foo())))

    def test_error_check(self):
        """ Make sure FunctionalWriter error check catches what we are expecting """
        with self.assertRaises(ValueError):
            self.w + self.w.indent()


if __name__ == '__main__':
    unittest.main()
