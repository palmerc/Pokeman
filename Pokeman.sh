#!/usr/bin/env bash

set -x

POKE_PROJECT_DIR=/Users/palmerc/PycharmProjects/Pokeman
echo -n "### Updating Pokemon - "
date
pushd ${POKE_PROJECT_DIR}
source ~/.bash_profile
pyenv exec python3 main.py

