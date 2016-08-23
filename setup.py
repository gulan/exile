#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

import sys
from setuptools import setup, find_packages

NAME = "exile"
DESCRIPTION = "Replace a directory with a symlink to a copy of it."
VERSION = "0.2.2"
AUTHOR = "gulan"
AUTHOR_EMAIL = "glen.wilder@gmail.com"

setup(
    name = NAME,
    version = VERSION,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    description = DESCRIPTION,
    packages = ['exile', 'test'],
    test_suite = 'test.test_action',
    scripts = ['occ', 'ez_setup.py'])
