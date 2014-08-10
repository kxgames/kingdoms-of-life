#!/usr/bin/env sh

for distribution in $@; do
    pip install --editable $distribution
done
