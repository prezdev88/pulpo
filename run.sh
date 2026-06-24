#!/bin/bash

detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    else
        echo "unknown"
    fi
}

# --- NVM check ---
export NVM_DIR="$HOME/.nvm"

nvm_available() {
    [ -s "$NVM_DIR/nvm.sh" ]
}

install_nvm() {
    echo "Installing nvm via the official install script..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
}

if ! nvm_available; then
    echo "nvm is not available on this system."
    read -p "Do you want to install it now? [y/N]: " answer
    case "$answer" in
        [yY]|[yY][eE][sS])
            install_nvm
            if ! nvm_available; then
                echo "Error: nvm installation failed. nvm was not installed." >&2
                exit 1
            fi
            ;;
        *)
            echo "nvm is required to run this application. Aborting." >&2
            exit 1
            ;;
    esac
fi

# Load NVM
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Use the installed node version
nvm use v26.3.1

# --- npm check ---
npm_available() {
    command -v npm >/dev/null 2>&1
}

install_npm() {
    local distro
    distro=$(detect_distro)

    case "$distro" in
        arch|manjaro|endeavouros|garuda|cachyos)
            echo "Detected distro: Arch-based ($distro)"
            sudo pacman -S --needed npm
            ;;
        debian|ubuntu|linuxmint|pop|elementary|zorin)
            echo "Detected distro: Debian-based ($distro)"
            sudo apt update && sudo apt install -y npm
            ;;
        fedora|rhel|centos|rocky|almalinux)
            echo "Detected distro: RedHat-based ($distro)"
            sudo dnf install -y npm
            ;;
        opensuse*|sles)
            echo "Detected distro: openSUSE-based ($distro)"
            sudo zypper install -y npm
            ;;
        *)
            echo "Unrecognized distro ($distro). Please reinstall Node.js via nvm to get npm."
            nvm install --reinstall-packages-from=node v26.3.1
            ;;
    esac
}

if ! npm_available; then
    echo "npm is not available on this system."
    read -p "Do you want to install it now? [y/N]: " answer
    case "$answer" in
        [yY]|[yY][eE][sS])
            install_npm
            if ! npm_available; then
                echo "Error: npm installation failed. npm was not installed." >&2
                exit 1
            fi
            ;;
        *)
            echo "npm is required to run this application. Aborting." >&2
            exit 1
            ;;
    esac
fi

# --- Electron check ---
electron_available() {
    # 1. Electron as a local project dependency
    if [ -x "./node_modules/.bin/electron" ]; then
        return 0
    fi
    # 2. Electron installed globally
    if command -v electron >/dev/null 2>&1; then
        return 0
    fi
    return 1
}

install_electron() {
    local distro
    distro=$(detect_distro)

    case "$distro" in
        arch|manjaro|endeavouros|garuda|cachyos)
            echo "Detected distro: Arch-based ($distro)"
            sudo pacman -S --needed electron
            ;;
        debian|ubuntu|linuxmint|pop|elementary|zorin)
            echo "Detected distro: Debian-based ($distro)"
            sudo apt update && sudo apt install -y electron
            ;;
        fedora|rhel|centos|rocky|almalinux)
            echo "Detected distro: RedHat-based ($distro)"
            sudo dnf install -y electron
            ;;
        opensuse*|sles)
            echo "Detected distro: openSUSE-based ($distro)"
            sudo zypper install -y electron
            ;;
        *)
            echo "Unrecognized distro ($distro). Installing Electron as a local npm dependency instead."
            npm install --save-dev electron
            ;;
    esac
}

if ! electron_available; then
    echo "Electron is not available on this system."
    read -p "Do you want to install it now? [y/N]: " answer
    case "$answer" in
        [yY]|[yY][eE][sS])
            install_electron
            if ! electron_available; then
                echo "Error: Electron installation failed. Electron was not installed." >&2
                exit 1
            fi
            ;;
        *)
            echo "Electron is required to run this application. Aborting." >&2
            exit 1
            ;;
    esac
fi

# Start the Electron app
npm start