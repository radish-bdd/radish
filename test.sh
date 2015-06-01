#!/bin/bash

NOSEBIN="env/bin/nosetests"
if [ ! -f "$NOSEBIN" ]; then
    NOSEBIN=nosetests
fi

$NOSEBIN -v tests/unit/ --rednose --with-cover --cover-package=radish/ --cover-erase
