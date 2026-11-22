#!/bin/sh

set -e

if [[ "$PWD" != */_newtxtt ]]; then
    echo "Error: expected _newtxtt, got $PWD" >&2
    exit 1
fi

echo "Building pdf in newtxtt/doc with TEXINPUTS=\".:..//:\" ..."

cd newtxtt/doc

# export shell variables, locations are relative to where
# (pdf)latex is exercised

export TEXINPUTS=".:../tex//:"
export TFMFONTS="../tfm//:"
export T1FONTS="../type1//:"
export ENCFONTS="../enc//:"
export TEXFONTMAPS="../map//:"

latexmk -halt-on-error -interaction=batchmode -pdf newtxtt-doc.tex

echo "... done"

# Local variables:
# coding: utf-8
# End:
