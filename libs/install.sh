#!/usr/bin/env sh

if [ $# -eq 0 ]; then
    echo "Usage: install.sh <libraries>..."
    exit 1
fi

for distribution in $@; do
    pip install --editable $distribution
done
