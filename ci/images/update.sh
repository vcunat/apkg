#!/bin/bash
# build and upload docker image(s) into apkg registry
#
# this is a simple wrapper around build.sh and update.sh

if [[ $# -le 0 ]]; then
    echo "usage: $0 IMAGE..."
    exit 1
fi
set -e

for IMAGE in "$@"
do
    echo "Building $IMAGE..."
    ./build.sh $IMAGE
    echo "Pushing $IMAGE..."
    ./push.sh $IMAGE
done

