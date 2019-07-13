#!/bin/sh

ROOT=$(dirname "$0")
TESTS_ROOT=exploratory

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

cd "${ROOT}/${TESTS_ROOT}" || exit 1

${RADISH_BIN} --version
whereis ${RADISH_BIN}

for t in *; do
    if [ -f "${t}/disabled" ]; then
        # skip all disabled tests
        continue
    fi

    export COVERAGE_FILE=${BASE_COVERAGE_FILE}.${t}

    FEATURES_DIR="features"
    TESTS_DIR="tests/"
    CMDLINE_FILE="cmdline"
    TEST_CMDLINE_FILE="test-cmdline"

    cd "${t}" || exit 1

    if [ -n "$(ls -A "${TESTS_DIR}" 2>/dev/null)" ]; then
        # check if custom cmdline arguments are specified
        custom_cmdline_args=""
        if [ -f "${TEST_CMDLINE_FILE}" ]; then
            custom_cmdline_args=$(cat "${TEST_CMDLINE_FILE}")
        fi

        echo "${custom_cmdline_args}" | PYTHONPATH=. xargs coverage run -a --rcfile="${COVERAGE_RC}" --source=radish "${RADISH_TEST_BIN}" matches "${TESTS_DIR}"/*
        if [ $? -ne 0 ]; then
            echo "Exploratory tests from '${t}' failed to match steps with status $?"
            exit 1
        fi
    fi

    # check if custom cmdline arguments are specified
    custom_cmdline_args=""
    if [ -f "${CMDLINE_FILE}" ]; then
        custom_cmdline_args=$(cat "${CMDLINE_FILE}")
    fi

    echo "${custom_cmdline_args}" | PYTHONPATH=. xargs coverage run -a --rcfile="${COVERAGE_RC}" --source=radish "${RADISH_BIN}" "${FEATURES_DIR}"
    if [ $? -ne 0 ]; then
        echo "Exploratory tests from '${t}' failed with status $?"
        exit 1
    fi

    cd - || exit 1
done
