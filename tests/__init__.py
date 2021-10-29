import logging

# Set log level for debugging tests here
import os

LOGLEVEL = logging.INFO
cwd = os.path.abspath(os.path.dirname(__file__))
datadir = os.path.join(cwd, 'data')

# Set this to False if you want to make sure some of the big inputs work
SKIP_LONG_TESTS = True
