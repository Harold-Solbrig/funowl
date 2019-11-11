import unittest
import sys
from typing import Tuple, Optional, Dict, Callable

import os
import requests


class ValidationTestCase(unittest.TestCase):
    repo_base: str = None           # Base URI or directory name
    file_suffix: str = None         # file suffix (e.g. ".shex")
    start_at: Optional[str] = ""    # Start at or after this
    skip: Dict[str, str] = dict()   # Filename / reason for skip array
    validation_function: Callable[[str], bool] = None  #
    single_file: bool = False       # True means process exactly one file
    stop_on_error: bool = False      # True means stop once you encounter an error
    number_of_errors: int = 0       # Number of errors detected

    @classmethod
    def make_test_function(cls, url):
        def test(self):
            if not cls.stop_on_error or not cls.number_of_errors:
                rval = cls.validation_function(url)
                if not rval:
                    cls.number_of_errors += 1
                    self.fail("Validation failure")
        return test

    @classmethod
    def build_test_harness(cls) -> None:
        started = not bool(cls.start_at)
        cls.number_of_errors = 0
        for fname, fpath in (cls.enumerate_http_files(cls.repo_base)
                if ':' in cls.repo_base else cls.enumerate_directory(cls.repo_base)):
            if fname.endswith(cls.file_suffix):
                if started or fname.startswith(cls.start_at):
                    if fname not in cls.skip:
                        started = True
                        test_func = cls.make_test_function(fpath)
                        setattr(cls, 'test_{0}'.format(fname.rsplit('.', 1)[0]), test_func)
                        if cls.single_file:
                            break
                    else:
                        print(f"***** Skipped: {fname} - {cls.skip[fname]}")

    @staticmethod
    def enumerate_http_files(url) -> Tuple[str, str]:
        resp = requests.get(url)
        if resp.ok:
            for f in resp.json():
                yield f['name'], f['download_url']
        else:
            print("Error {}: {}".format(resp.status_code, resp.reason), file=sys.stderr)

    @staticmethod
    def enumerate_directory(dir_) -> Tuple[str, str]:
        for fname in os.listdir(dir_):
            fpath = os.path.join(dir_, fname)
            if os.path.isfile(fpath):
                yield fname, fpath

    def blank_test(self):
        self.assertTrue(True)
