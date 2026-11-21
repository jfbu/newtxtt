# newtxtt 1.060 2026-11-20 #

This repository documents the work done on November 20, 2026, starting with
`newtxtt 1.059 2024-03-12`, the last release authored by Michael Sharpe, the
creator of the `newtxtt` package, to produce `newtxtt 1.060 2026-11-20`.

The version `1.059` was broken with TS1 encoding ("TeX companion fonts") and
the slanted shape, and also for all shapes of the variable width variant.  For
example an English LaTeX document using `\usepackage[ttzdefault]{newtxtt}`
broke with a missing font error at the first `\item` in an `itemize`
environnment.  This is because `\textbullet` belongs to a TS1 encoded font.
Characters such as `©` would also break the build.

The human author did not have access to Michael's original development
directories and instructed ChatGPT to work directly on the files extracted
from a `newtxtt.zip` archive downloaded some days earlier from a CTAN mirror.

For a detailed list of all improvements refer to
[`newtxtt/doc/newtxtt-1060-2026-11-20.md`](newtxtt/doc/newtxtt-1060-2026-11-20.md).

## Maintenance

The `newtxtt` package is currently (November 20, 2026) without maintainer.

The repository https://github.com/LaTeX-Package-Repositories/msharpe
coordinates the maintenance of the packages originally authored by Michael Sharpe.
As the owner of this GitHub repository will not take over maintenance
please use https://github.com/LaTeX-Package-Repositories/msharpe/issues
as the issue tracker.

This repository was created only to record the work done from `1.059` to `1.060`.
It will probably not track the changes at
https://github.com/LaTeX-Package-Repositories/msharpe/tree/main/newtxtt.

Note that the tag `1.060-2026-11-20` points here at a version which differs
slightly (only via some metadata in the `README` and files in `doc/`) from the
one which, on 2026-11-21 is at
https://github.com/LaTeX-Package-Repositories/msharpe/tree/main/newtxtt.

It is the latter which got uploaded to CTAN as `1.060`.

Here is some info if someone takes over maintenance and the
LaTeX-Package-Repositories version is still at `1.060`.  The directory
`tools/` contain some Python scripts and some audit outputs which
were used to ensure in particular that no glyph metric was modified
during the fixes.  The original `1.059` release is embedded in two
ways in the repository: first there is the archived file
[`newtxtt-1.059-2024-03-12.zip`](newtxtt-1.059-2024-03-12.zip),
second the initial commit (tag `1.059-2024-03-12`) holds in
`newtxtt/` that release.

For the Makefile `test` target to work, it is needed to first populate a
directory `original/` with the original release which can be done from
unzipping with destination `original/` the
[`newtxtt-1.059-2024-03-12.zip`](newtxtt-1.059-2024-03-12.zip) archive
(so there will be `original/newtxtt/`).

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

