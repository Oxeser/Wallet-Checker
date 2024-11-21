#!/bin/bash

RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
CYAN="\033[0;36m"
RESET="\033[0m"

echo -e "${CYAN}Wallet Checker Setup Script${RESET}"

OS=""
if [ "$(uname)" == "Linux" ]; then
    if [ -f "/data/data/com.termux/files/usr/bin/apt" ]; then
        OS="Termux"
    else
        OS="Linux"
    fi
elif [[ "$(uname -o)" == *"Msys"* || "$(uname -o)" == *"Cygwin"* ]]; then
    OS="Windows"
else
    echo -e "${RED}Unsupported operating system.${RESET}"
    exit 1
fi

function check_python() {
    if ! command -v python3 &> /dev/null; then
        if [ "$OS" == "Termux" ]; then
            pkg install python -y
        elif [ "$OS" == "Linux" ]; then
            sudo apt update && sudo apt install python3 python3-pip -y
        elif [ "$OS" == "Windows" ]; then
            echo -e "${RED}Install Python3 manually from https://www.python.org/downloads/.${RESET}"
            exit 1
        fi
    fi

    if ! command -v pip3 &> /dev/null; then
        if [ "$OS" == "Termux" ] || [ "$OS" == "Linux" ]; then
            sudo apt install python3-pip -y
        else
            echo -e "${RED}Install pip3 manually.${RESET}"
            exit 1
        fi
    fi
}

function install_dependencies() {
    pip3 install --upgrade pip
    pip3 install termcolor pyfiglet requests mnemonic bip32utils
}

function check_git() {
    if ! command -v git &> /dev/null; then
        if [ "$OS" == "Termux" ]; then
            pkg install git -y
        elif [ "$OS" == "Linux" ]; then
            sudo apt update && sudo apt install git -y
        elif [ "$OS" == "Windows" ]; then
            echo -e "${RED}Install Git manually from https://git-scm.com/.${RESET}"
            exit 1
        fi
    fi
}

function post_install_message() {
    echo -e "${GREEN}Setup completed successfully!${RESET}"
}

check_python
check_git
install_dependencies
post_install_message
python3 main.py
