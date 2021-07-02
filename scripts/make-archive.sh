#!/bin/bash
# create archive from current source using git
set -e

VERSION=$(python3 -m apkg --version)
if [ -z "$VERSION" ]; then
    echo "failed to retrieve current apkg version :("
    exit 1
fi
OUTPATH=pkg/archives/dev
NAMEVER=apkg-v$VERSION
ARCHIVE=$NAMEVER.tar.gz
ARPATH=$OUTPATH/$ARCHIVE

mkdir -p "$OUTPATH"
git archive --format tgz --output $ARPATH --prefix $NAMEVER/ HEAD

# apkg expects stdout to list archive files
echo $ARPATH
