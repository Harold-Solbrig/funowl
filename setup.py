#!/usr/bin/env python
import sys
from logging import warn

from setuptools import setup

if sys.version_info < (3, 8, 0):
    warn(f"FunOwl needs python 3.8 or later.  Current version: {sys.version_info}")

setup(
    setup_requires=['pbr'],
    pbr=True,
)
