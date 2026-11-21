# newtxtt 1.060 2026-11-20 #

This documents the repairs done by ChatGPT on November 20, 2026,
to Michael Sharpe's `newtxttt 1.059 2024-03-12` which was the
last previous release.

The `newtxtt` package is currently without maintainer.

This author will not take over maintenance.  Issues will not
be handled, but can be recorded here until someone volunteers,
and forks this repository.

The author did not have access to Michael's original development
directories and let ChatGPT work directly on a `newtxtt.zip`
downloaded from a CTAN mirror some days earlier.

People taking over maintenance should execute `make original`
in their git clone so that `original/newtxtt/` contains the files
of the `1.059 2024-03-12` distribution.  Or they can directly
unzip the committed file `newtxtt-1.059-2024-03-12.zip`.
This structure is needed for some of the tests triggered by
`make test` in particular checking that  the glyph metrics have
not been changed compared to the original distribution.

The repository https://github.com/LaTeX-Package-Repositories/msharpe
coordinates the maintenance of the packages originally by Michael Sharpe.

**ANY ISSUE CREATED HERE SHOULD CONTAIN A PING `@jfbu` SO THAT I
GET THE NOTIFICATION**

## Installation

First, execute `make CTAN/newtxtt.tds.zip`.

To install the corrected version locally, execute from `CTAN/`:

    unzip -o newtxtt.tds.zip -d "$(kpsewhich -var-value=TEXMFHOME)"

If `newtxtt` is already installed and its font map enabled in your
TeX Live distribution, no further action is required. The font map
file is unchanged from version 1.059.

Otherwise, enable the font map:

    updmap-user --enable Map=newtxtt.map

Be aware that running `updmap-user` creates personal font maps
which take precedence over the system-generated ones.

## Uninstallation

If you enabled the font map manually during installation, disable
it before removing the files:

    updmap-user --disable newtxtt.map

To remove the locally installed version:

    cd "$(kpsewhich -var-value=TEXMFHOME)" &&
    rm -rf tex/latex/newtxtt \
           doc/fonts/newtxtt \
           fonts/tfm/public/newtxtt \
           fonts/type1/public/newtxtt \
           fonts/enc/dvips/newtxtt \
           fonts/map/dvips/newtxtt

TeX Live will then revert to using its own installed version of
`newtxtt`, if present.


## License

The fonts are licensed under the GNU General Public License,
version 3 (GPL-3.0).

The LaTeX support files are subject to the LaTeX Project Public
License (LPPL), version 1.3.

See [newtxtt/README](newtxtt/README) for the original author's
detailed licensing terms.

