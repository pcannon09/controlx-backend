#!/bin/bash

# PCANNON OPEN.SH v1.0S - FROM PCANNON PROJECT STANDARDS
# STANDARD: 20250608
# https://github.com/pcannon09/pcannonProjectStandards
# NOTES:
# Modified to open `tests/` dir

defaultEdit="$1" # Set the default editor in parameter $1 (such as: code, vim, nvim, ...)

if [ "$1" == "" ]; then
	defaultEdit="nvim"
fi

$defaultEdit main.py $(find src/*.py -type f)

