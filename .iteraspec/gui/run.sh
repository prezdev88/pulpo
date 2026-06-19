#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"
PORT="${PORT:-8001}"

cd "${ROOT_DIR}"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  printf 'No se encontró el intérprete %s\n' "${PYTHON_BIN}" >&2
  exit 1
fi

if [ ! -d "${VENV_DIR}" ]; then
  printf 'Creando entorno virtual en %s\n' "${VENV_DIR}"
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

if [ ! -x "${VENV_DIR}/bin/python" ]; then
  printf 'El entorno virtual no contiene un intérprete ejecutable.\n' >&2
  exit 1
fi

if ! "${VENV_DIR}/bin/python" -c 'import fastapi, uvicorn' >/dev/null 2>&1; then
  printf 'Instalando dependencias de la GUI\n'
  "${VENV_DIR}/bin/pip" install -r requirements.txt
fi

printf 'Levantando IteraSpec GUI Viewer en http://127.0.0.1:%s\n' "${PORT}"
PORT="${PORT}" "${VENV_DIR}/bin/python" app.py
