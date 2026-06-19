#!/bin/bash

# Cargar NVM
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Usar la versión de node instalada
nvm use v26.3.1

# Iniciar la aplicación Electron
npm start
