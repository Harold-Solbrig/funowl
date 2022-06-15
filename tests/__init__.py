import logging
import rdflib

# Set log level for debugging tests here
import os

LOGLEVEL = logging.INFO
cwd = os.path.abspath(os.path.dirname(__file__))
datadir = os.path.join(cwd, 'data')

# Set this to False if you want to make sure some of the big inputs work
SKIP_LONG_TESTS = True

# rdflib 6.1.1 has a LONG list of pre-assigned prefixes.  This breaks some of our tests and the rdflib
# community promises to fix it (some day...).  For now, we won't run tests on this version
RDFLIB_PREFIXES_ARE_BROKEN = rdflib.__version__ == "6.1.1"
PREFIXES_BROKEN_MESSAGE = "rdflib 6.1.1 emits a LOT of prefixes.  Test skipped!"
