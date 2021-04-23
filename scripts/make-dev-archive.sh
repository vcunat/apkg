#!/bin/bash
#
# Create apkg archive and print path to it.

DISTDIR=dist

rm -rf "$DISTDIR"
python3 -m build --sdist
ls dist/apkg-*.tar.gz
