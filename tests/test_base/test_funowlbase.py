import unittest
from dataclasses import dataclass, fields, field
from typing import List, Union, Optional

# This has to be global for the cast forwards to work correctly
from funowl.base.fun_owl_base import FunOwlBase
from funowl.base.fun_owl_choice import FunOwlChoice
from funowl.base.list_support import empty_list_wrapper
from funowl.terminals.TypingHelper import proc_forwards
from funowl.writers.FunctionalWriter import FunctionalWriter
from tests.utils.base import TestBase


@dataclass
class C1(FunOwlBase):
    instnum: int
    foos: List["C1"] = field(default_factory=list)

    def to_functional(self, w: FunctionalWriter) -> FunctionalWriter:
        return w.func(self, lambda: w.br().indent().concat(self.instnum, ':', sep='').outdent().iter(self.foos))

proc_forwards(C1, globals())
for f in fields(C1):
    if f.name == 'foos':
        f.default_factory = empty_list_wrapper(C1)


# noinspection PyTypeChecker
class FunOwlBaseTestCase(TestBase):

    def test_is_valid(self):
        """ _is_valid determines whether an object could be coerced into an instance of the class """
        class Foo(FunOwlBase):
            def _is_valid(cls, instance) -> bool:
                return isinstance(instance, str) or FunOwlBase._is_valid(cls, instance)

        class Foo2(Foo):
            pass

        self.assertTrue(isinstance('abc', Foo))
        self.assertFalse(isinstance(17, Foo))
        self.assertTrue(isinstance(Foo2(), Foo))
        self.assertTrue(isinstance(Foo2(), Foo2))
        self.assertFalse(isinstance(Foo(), Foo2))

    def test_iter(self):

        class Foo2(FunOwlBase):
            inst: int = 0

            def __init__(self):
                Foo2.inst = Foo2.inst + 1
                self.instnum = Foo2.inst

            def to_functional(self, wr: FunctionalWriter) -> FunctionalWriter:
                return wr + f"I{self.instnum}"

        @dataclass
        class Foo(FunOwlBase):
            v: List[Foo2] = empty_list_wrapper(Foo2)

            def to_functional(self, wr: FunctionalWriter) -> FunctionalWriter:
                return wr.iter(self.v, f=lambda e:  wr.hardbr() + e)

            def to_functional2(self, wr: FunctionalWriter) -> FunctionalWriter:
                return wr.hardbr().indent().iter(self.v).outdent()

        foo = Foo()
        self.assertEqual('', str(foo.to_functional(self.w)))
        foo.v.append(Foo2())
        self.assertEqual('\n    I1', str(foo.to_functional(self.w)))
        self.w.reset()
        self.assertEqual('\n        I1', str(foo.to_functional(self.w.indent())))
        self.w.reset()
        foo.v.append(Foo2())
        foo.v.append(Foo2())
        self.assertEqual('\n    I1\n    I2\n    I3', str(foo.to_functional(self.w)))
        self.w.reset()
        self.assertEqual('\n        I1\n        I2\n        I3', str(foo.to_functional2(self.w)))

    def test_list_cardinality(self):

        @dataclass
        class Foo(FunOwlBase):
            v: List[int] = empty_list_wrapper(int)

        x = Foo()
        self.assertEqual(x, x.list_cardinality(x.v, 'v', 0))
        with self.assertRaises(ValueError):
            x.list_cardinality(x.v, 'v', 1)
        self.assertEqual('FunOwlBaseTestCase.test_list_cardinality.<locals>.Foo(v=[])', str(x.to_functional(self.w)))

    def test_type_casts(self):
        x = C1(112)
        self.assertEqual("C1(\n    112:\n)", str(x.to_functional(self.w)))
        self.w.reset()
        x = C1(113, [x])
        # Note: this seems odd -- not sure I can justify why it does what it does, but it does verify that
        # that we haven't broken anything.
        self.assertEqual("C1(\n    113:\n        C1(\n        112:\n    )\n)", str(x.to_functional(self.w)))

        @dataclass()
        class CU(FunOwlBase):
            v: Optional[Union[int, str]] = None

            def to_functional(self, wr: FunctionalWriter) -> FunctionalWriter:
                return wr + f"INT: {self.v}" if isinstance(self.v, int) else f"STR: '{self.v}'"

        self.w.reset()
        self.assertEqual('INT: 117', str(CU(117).to_functional(self.w)))
        self.w.reset()
        self.assertEqual("STR: 'abc'", str(CU('abc').to_functional(self.w)))
        self.w.reset()
        with self.assertRaises(TypeError):
            CU(123.4).to_functional(self.w)

        @dataclass()
        class CC(FunOwlChoice):
            v: Union[int, str, CU]

        x = CC(42)
        self.assertEqual('42', str(x.to_functional(self.w.reset())))
        x.v = -44
        self.assertEqual('-44', str(x.to_functional(self.w.reset())))
        x = CC(CU(45))
        self.w.reset()
        self.assertEqual('INT: 45', str(x.to_functional(self.w)))
        x.v = CU(-45)
        self.w.reset()
        self.assertEqual('INT: -45', str(x.to_functional(self.w)))
        with self.assertRaises(TypeError):
            CC(x)
        with self.assertRaises(TypeError):
            x.v = CC(117)
        self.assertTrue(isinstance(44, CC))
        self.assertTrue(isinstance(CC('abc'), CC))
        self.assertFalse(isinstance(12.3, CC))

    def test_type_casts2(self):
        @dataclass
        class CI(FunOwlChoice):
            v: Optional[int] = None

            def to_functional(self, wr: FunctionalWriter) -> FunctionalWriter:
                return (wr + "I: ").opt(self.v)

        @dataclass
        class CS(FunOwlChoice):
            v: Optional[str] = None

            def to_functional(self, wr: FunctionalWriter) -> FunctionalWriter:
                return (wr + "S: ").opt(self.v)

        @dataclass()
        class CU(FunOwlChoice):
            v: Union[CI, CS]

        x = CU(17)
        self.assertEqual('I:  17', str(x.to_functional(self.w)))
        x = CU('abc')
        self.w.reset()
        self.assertEqual('S:  abc', str(x.to_functional(self.w)))
        with self.assertRaises(TypeError):
            CU(object())

    def test_type_casts3(self):
        @dataclass
        class CI(FunOwlBase):
            v1: List[str]

            def to_functional(self, wr: FunctionalWriter) -> FunctionalWriter:
                return wr.iter(self.v1)

        x = CI("sam")
        self.assertEqual(['sam'], x.v1)
        self.assertEqual('    sam', str(x.to_functional(self.w)))
        self.w.reset()
        x = CI(["joe", "bob"])
        self.assertEqual(['joe', "bob"], x.v1)
        self.assertEqual('    joe\n    bob', str(x.to_functional(self.w)))
        self.w.reset()
        x = CI([])
        x.v1 = "fred"
        self.assertEqual(['fred'], x.v1)
        self.assertEqual('    fred', str(x.to_functional(self.w)))
        self.w.reset()
        x = CI([])
        x.v1 = ["jane", "sally"]
        self.assertEqual(['jane', 'sally'], x.v1)
        self.assertEqual('    jane\n    sally', str(x.to_functional(self.w)))


if __name__ == '__main__':
    unittest.main()
