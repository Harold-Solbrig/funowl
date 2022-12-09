import argparse
import os.path
import unittest
from contextlib import redirect_stdout
from io import StringIO
from typing import List

from funowl import cli

CWD = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(CWD, 'data')

UPDATE_OUTPUT_FILES = True
CLI_NAME = 'cli'


# Override the annoying argparse insistence on doing a sys.exit after help printed
class HelpPrintedException(Exception):
    pass


def exit(parser, status=0, message=None):
    raise HelpPrintedException(message)


class CLITestCase(unittest.TestCase):
    @staticmethod
    def _file_or_text(inp: str) -> str:
        if '\n' in inp:
            return inp
        with open(os.path.join(TEST_DATA_DIR, inp)) as f:
            return f.read()

    def _compare_output(self, expected, actual) -> bool:
        e_str = self._file_or_text(expected)
        a_str = self._file_or_text(actual)
        if e_str == a_str:
            return True
        if UPDATE_OUTPUT_FILES and e_str != expected:       # expected is a file name
            outfile = os.path.join(TEST_DATA_DIR, expected)
            with open(outfile, 'w') as f:
                f.write(actual)
            print(f"File: {os.path.relpath(outfile, CWD)} has been updated")
        return False

    def _generate_file(self, infilename: str, outfilename: str, addl_params: List[str] = None) -> None:
        args = [os.path.join(TEST_DATA_DIR, infilename), os.path.join(TEST_DATA_DIR, outfilename)]
        if addl_params:
            args += addl_params
        cli.evaluate_cli(args, CLI_NAME)

    def test_cli_help(self):
        """ Test help function """
        orig_exit = argparse.ArgumentParser.exit
        argparse.ArgumentParser.exit = exit
        with self.assertRaises(HelpPrintedException):
            out_txt = StringIO()
            with redirect_stdout(out_txt):
                cli.evaluate_cli("-h", CLI_NAME)
        argparse.ArgumentParser.exit = orig_exit
        if not self._compare_output('cli_help.txt', out_txt.getvalue()):
            self.fail(msg="Help output has changed!")

    def test_cli_conversion(self):
        """ Test basic conversion  """
        self._generate_file('pizza.owl', 'pizza_out.ttl')

    def test_auto_output_type(self):
        """ Test that output file name suffixes are recognized """
        # Should generate json-ld
        self._generate_file('pizza.owl', 'pizza_out.jsonld')
        # Should generate owl (explicit)
        self._generate_file('pizza.owl', 'pizza_out2.jsonld', ["-f", "hext"])
        # Not sure
        self._generate_file('pizza.owl', 'pizza_out3.foo')

    def test_cli_options(self):
        """ Make sure that file name suffixes are recognized """
        cli.evaluate_cli(
            [os.path.join(TEST_DATA_DIR, 'basic.owl'), os.path.join(TEST_DATA_DIR, 'basic_out.n3')],
            CLI_NAME)

        # Dots shouldn't be printed if "-np" or output is to stdout
        output = StringIO()
        with redirect_stdout(output):
            cli.evaluate_cli(
                [os.path.join(TEST_DATA_DIR, 'pizza.owl'), os.path.join(TEST_DATA_DIR, 'pizza_out4.n3'), '-np'],
                CLI_NAME)
            cli.evaluate_cli(
                [os.path.join(TEST_DATA_DIR, 'pizza.owl')],
                CLI_NAME)
        self.assertNotIn(".....", output.getvalue())


if __name__ == '__main__':
    unittest.main()
