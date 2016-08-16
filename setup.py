#!/usr/bin/env python

import sys
from distutils.core import setup

NAME = "exile"
DESCRIPTION = "Replace a directory with a symlink to a copy of it."
VERSION = "0.0.5"
AUTHOR = "gulan"
AUTHOR_EMAIL = "glen.wilder@gmail.com"


if __name__ == "__main__":
    setup(
        name = NAME,
        version = VERSION,
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        description = DESCRIPTION,
        scripts = ["exile","pardon"])

    sys.exit(0)
