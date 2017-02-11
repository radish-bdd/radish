#!/bin/sh

ROOT=$(dirname "$0")
TESTS_ROOT=functional

RADISH_BIN=radish/main.py
RADISH_TEST_BIN=radish/main.py

BASE_COVERAGE_FILE=$(pwd)/.coverage
COVERAGE_RC=$(pwd)/.coveragerc

if [ -n "${VIRTUAL_ENV}" ]; then
    # we are running inside a python virtualenv
    VIRTUAL_ENV_BIN=${VIRTUAL_ENV}/bin
    RADISH_BIN=${VIRTUAL_ENV_BIN}/radish
    RADISH_TEST_BIN=${VIRTUAL_ENV_BIN}/radish-test
fi

cd "${ROOT}/${TESTS_ROOT}"

for t in *; do
    export COVERAGE_FILE=${BASE_COVERAGE_FILE}.${t}

    BASE_DIR="${t}/radish"
    FEATURES_DIR="${t}/features"
    MATCHES_FILE="${t}/tests/radish-matches.yml"

    if [ -f "${MATCHES_FILE}" ]; then
        coverage run -a --rcfile="${COVERAGE_RC}" --source=radish "${RADISH_TEST_BIN}" matches -b "${BASE_DIR}" "${MATCHES_FILE}"
        if [ $? -ne 0 ]; then
            echo "Functional tests from '${t}' failed to match steps with status $?"
            exit 1
        fi
    fi

    PYTHONPATH="${t}" coverage run -a --rcfile="${COVERAGE_RC}" --source=radish "${RADISH_BIN}" -b "${BASE_DIR}" "${FEATURES_DIR}"
    if [ $? -ne 0 ]; then
        echo "Functional tests from '${t}' failed with status $?"
        exit 1
    fi
done
