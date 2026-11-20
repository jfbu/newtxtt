#!/bin/sh

set -e

if [[ "$PWD" != */_newtxtt ]]; then
    echo "Error: expected _newtxtt, got $PWD" >&2
    exit 1
fi

echo "Building pdf in newtxtt/doc with TEXINPUTS=\".:..//:\" ..."

cd newtxtt/doc

# export TEXINPUTS="./subdirectory//:${TEXINPUTS:-}:"

export TEXINPUTS=".:..//:"
export TFMFONTS=".:..//:"
export T1FONTS=".:..//:"
export ENCFONTS=".:..//:"
export TEXFONTMAPS=".:..//:"

latexmk -halt-on-error -interaction=batchmode -pdf newtxtt-doc.tex

echo "... done"

# Local variables:
# coding: utf-8
# End:
