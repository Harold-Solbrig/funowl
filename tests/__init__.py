import logging

# Set log level for debugging tests here
import os

LOGLEVEL = logging.INFO
cwd = os.path.abspath(os.path.dirname(__file__))
datadir = os.path.join(cwd, 'data')