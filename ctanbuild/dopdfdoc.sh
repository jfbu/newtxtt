#!/bin/sh

set -e

# echo "THIS \"$(pwd)\" SHOULD BE \"_newtxtt/ctanbuild\"" 

if [[ "$PWD" != */_newtxtt/ctanbuild ]]; then
    echo "Error: expected newtxtt/ctanbuild, got $PWD" >&2
    exit 1
fi

echo "Building pdf in ctanbuild/newtxtt/doc with TEXINPUTS=\".:..//:\" ..."

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
