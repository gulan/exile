#!/usr/bin/env python

import sys
from distutils.core import setup

NAME = "exile"
DESCRIPTION = "Move and Symlink directories"
VERSION = "0.0.1"
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
