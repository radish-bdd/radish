#!/bin/sh

ROOT=$(dirname "$0")
TESTS_ROOT=functional
RADISH_BASEDIR=radish
FEATURES_DIR=features

#export COVERAGE_FILE=$(pwd)/.coverage
BASE_COVERAGE_FILE=$(pwd)/.coverage
COVERAGE_RC=$(pwd)/.coveragerc

cd "$ROOT/$TESTS_ROOT"

for t in *; do
    export COVERAGE_FILE=${BASE_COVERAGE_FILE}.$t
    coverage run -a --rcfile=$COVERAGE_RC --source=radish ${1}/radish -b "$t/$RADISH_BASEDIR" "$t/$FEATURES_DIR"
    if [ $? -ne 0 ]; then
        echo "Functional tests from '$t' failed with status $?"
        exit 1
    fi
done
