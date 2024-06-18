#!/bin/bash

BASH_SCRIPT_NAME="$(basename $0)"

pushd "$(dirname $0)" >/dev/null || exit
SOURCE_DIR=$(pwd)
popd >/dev/null || exit

PYTHON_SCRIPT="${SOURCE_DIR}/${BASH_SCRIPT_NAME/_venv.sh/.py}"

VENV_DIR="${SOURCE_DIR}/.venv"
if [ ! -d  "${VENV_DIR}" ]; then
    python -m venv "${VENV_DIR}"
fi

source "${SOURCE_DIR}/.venv/bin/activate"
if [ -f "${SOURCE_DIR}/requirements.txt" ]; then
    pip --quiet --disable-pip-version-check install -r "${SOURCE_DIR}/requirements.txt"
fi

"${PYTHON_SCRIPT}" "$@"
deactivate

