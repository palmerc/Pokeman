#!/bin/bash

PYTHON_EXE=python3
PIP_EXE=pip3
BASH_SCRIPT_NAME="$(basename $0)"

if ! command -v ${PYTHON_EXE} &> /dev/null; then
    PYTHON_EXE=python
    PIP_EXE=pip
fi

pushd "$(dirname $0)" >/dev/null
SOURCE_DIR=$(pwd)
popd >/dev/null

PYTHON_SCRIPT="${SOURCE_DIR}/${BASH_SCRIPT_NAME/_venv.sh/.py}"

VENV_DIR="${SOURCE_DIR}/.venv"
if [ ! -d  "${VENV_DIR}" ]; then
    ${PYTHON_EXE} -m venv "${VENV_DIR}"
fi

source "${SOURCE_DIR}/.venv/bin/activate"
if [ -f "${SOURCE_DIR}/requirements.txt" ]; then
    ${PIP_EXE} --quiet --disable-pip-version-check install -r "${SOURCE_DIR}/requirements.txt"
fi

${PYTHON_EXE} "${PYTHON_SCRIPT}" "$@"

deactivate

