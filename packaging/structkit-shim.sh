#!/bin/bash
# Shim script for structkit CLI
# Executes structkit from the vendored Python environment

set -e

STRUCTKIT_HOME="/usr/lib/structkit"
PYTHON_BIN="${STRUCTKIT_HOME}/venv/bin/python"
STRUCTKIT_MODULE="${STRUCTKIT_HOME}/venv/bin/structkit"

if [ ! -f "${PYTHON_BIN}" ]; then
    echo "Error: structkit Python environment not found at ${STRUCTKIT_HOME}" >&2
    echo "Please reinstall structkit." >&2
    exit 1
fi

exec "${STRUCTKIT_MODULE}" "$@"
