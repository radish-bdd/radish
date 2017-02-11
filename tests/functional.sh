#!/bin/sh

ROOT=$(dirname "$0")
TESTS_ROOT=functional
RADISH_BASEDIR=radish
FEATURES_DIR=features
RADISH_BIN=radish/main.py
BASE_COVERAGE_FILE=$(pwd)/.coverage
COVERAGE_RC=$(pwd)/.coveragerc

if [ -n "${VIRTUAL_ENV}" ]; then
    # we are running inside a python virtualenv
    VIRTUAL_ENV_BIN=${VIRTUAL_ENV}/bin
    RADISH_BIN=${VIRTUAL_ENV_BIN}/radish
fi

cd "$ROOT/$TESTS_ROOT"

for t in *; do
    export COVERAGE_FILE=${BASE_COVERAGE_FILE}.$t
    coverage run -a --rcfile=$COVERAGE_RC --source=radish ${RADISH_BIN} -b "$t/$RADISH_BASEDIR" "$t/$FEATURES_DIR"
    if [ $? -ne 0 ]; then
        echo "Functional tests from '$t' failed with status $?"
        exit 1
    fi
done
