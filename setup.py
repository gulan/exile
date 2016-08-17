#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

import sys
# from distutils.core import setup
from setuptools import setup, find_packages

NAME = "exile"
DESCRIPTION = "Replace a directory with a symlink to a copy of it."
VERSION = "0.1.1"
AUTHOR = "gulan"
AUTHOR_EMAIL = "glen.wilder@gmail.com"


setup(
    name = NAME,
    version = VERSION,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    description = DESCRIPTION,
    # packages = find_packages(exclude=['test']),
    packages = ['test'],
    test_suite = 'test.test_action',
    scripts = ['exile', 'pardon', 'ez_setup.py'])
