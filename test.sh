#!/bin/bash

env/bin/nosetests -v tests/unit/ --rednose --with-cover --cover-package=radish/ --cover-erase
