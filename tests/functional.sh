#!/bin/sh

ROOT=`dirname $0`
TESTS_ROOT=functional
RADISH_BASEDIR=radish
FEATURES_DIR=features

cd $ROOT/$TESTS_ROOT

for t in `ls`; do
    radish -b $t/$RADISH_BASEDIR $t/$FEATURES_DIR
    if [ $? -ne 0 ]; then
        echo "Functional tests from '$t' failed with status $?"
        exit 1
    fi
done
