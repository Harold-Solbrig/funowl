import unittest
from typing import Union, List, Tuple, Dict, Any

from funowl import Class
from funowl.terminals.TypingHelper import is_union, is_dict, is_iterable, isinstance_, is_list

inst_union = Union[int, str, Class, Dict[str, str], dict, Tuple[int, str]]
inst_union_2 = Union[int, str, Class, Dict[str, str], Tuple[int, str]]


class TypingHelperTestCase(unittest.TestCase):

    def test_isinstance(self):
        self.assertTrue(isinstance_(int, Any))
        self.assertTrue(isinstance_(None, Any))
        self.assertTrue(isinstance_(Any, Any))

        self.assertTrue(isinstance_(17, inst_union))
        self.assertTrue(isinstance_("fred", inst_union))
        self.assertTrue(isinstance_(False, inst_union))

        self.assertTrue(isinstance_(Class("http://example.org"), inst_union))

        self.assertTrue(isinstance_({"k": 42}, inst_union))
        self.assertFalse(isinstance_({"k": 42}, inst_union_2))
        self.assertTrue(isinstance_({"k": "abc"}, inst_union_2))
        self.assertTrue(isinstance_({"k": "abc", "l": "def"}, inst_union_2))
        self.assertFalse(isinstance_({"k": "abc", "l": True}, inst_union_2))
        self.assertTrue(isinstance_({"k": "abc", "l": True}, Union[Dict]))
        self.assertTrue(isinstance_({"k": "abc", "l": True}, Union[dict]))
        self.assertTrue(isinstance_({}, inst_union_2))

        self.assertTrue(isinstance_((17, "a"), inst_union))
        self.assertFalse(isinstance_(("a", "a"), inst_union))

        self.assertTrue(isinstance_(([1,2,3], [True, False, True]), Tuple[List[int], List[bool]]))


    def test_is_union(self):
        self.assertTrue(is_union(Union[int, str]))
        self.assertFalse(is_union(int))
        self.assertFalse(is_union(List[str]))
        self.assertFalse(is_union(Class))
        self.assertFalse(is_union(Tuple[str, int, str]))
        self.assertFalse(is_union(Dict[str, str]))
        self.assertFalse(is_union(dict))
        self.assertFalse(is_union(list))

    def test_is_dict(self):
        self.assertFalse(is_dict(Union[int, str]))
        self.assertFalse(is_dict(int))
        self.assertFalse(is_dict(List[str]))
        self.assertFalse(is_dict(Class))
        self.assertFalse(is_dict(Tuple[str, int, str]))
        self.assertTrue(is_dict(Dict[str, str]))
        self.assertTrue(is_dict(dict))
        self.assertFalse(is_dict(list))
        
    def test_is_iterable(self):
        self.assertFalse(is_iterable(Union[int, str]))
        self.assertFalse(is_iterable(int))
        self.assertTrue(is_iterable(List[str]))
        self.assertFalse(is_iterable(Class))
        self.assertTrue(is_iterable(Tuple[str, int, str]))
        self.assertTrue(is_iterable(Dict[str, str]))
        self.assertTrue(is_iterable(dict))      # Surprising to discover that dict is iterable but...
        self.assertTrue(is_iterable(list))
        
    def test_is_list(self):
        self.assertFalse(is_list(Union[int, str]))
        self.assertFalse(is_list(int))
        self.assertTrue(is_list(List[str]))
        self.assertFalse(is_list(Class))
        self.assertFalse(is_list(Tuple[str, int, str]))
        self.assertFalse(is_list(Dict[str, str]))
        self.assertFalse(is_list(dict))
        self.assertTrue(is_list(list))


if __name__ == '__main__':
    unittest.main()
