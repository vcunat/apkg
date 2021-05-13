#!/bin/bash
# create archive from current source using git
set -e

VERSION=$(python3 -m apkg --version)
if [ -z "$VERSION" ]; then
    echo "failed to retrieve current apkg version :("
    exit 1
fi
NAMEVER=apkg-v$VERSION
ARCHIVE=$NAMEVER.tar.gz

git archive --format tgz --output $ARCHIVE --prefix $NAMEVER/ HEAD

# apkg expects stdout to list archive files
echo $ARCHIVE
