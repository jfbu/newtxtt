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

Unfortunately, a TeX coding error by the AI assistant escaped the human
supervisor's attention.  This was fixed in the follow-up release 1.061.

1.062 (2026-11-23) restored the "Changes in version 1.059" entry in
`newtxtt/README`, accidentally deleted in 1.060, and the original 2024
modification times of unchanged files in the `zip` archive.

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

## Testing

To run tests it is needed first to create and populate (once) an `original/`
directory.  Create it, then execute `unzip -d original
newtxtt-1.059-2024-03-12.zip`.  The original `1.059` release is also embedded
in the Git history as the `newtxtt/` directory for the initial commit which is
tagged `1.059-2024-03-12`.

- Use `make test-all` to execute both test suites described below.  It is
  done automatically by `make ctan`.

- Use `make test-audit` to check consistency between TFM metrics, encoding
  vectors, Type 1 outlines, map entries and FD declarations, and preservation
  of original font data from `1.059`.

- Use `make test-font-regression` to compile and verify the checked-in tests
  in `tests/`.  First, PDF files are obtained from `pdflatex` compilation.
  Then `.txt` files recording (in Python lists of strings) the observed PDF
  glyphs and, where checked, Unicode text, are produced using `pypdf`.  They
  are compared with the data in the `*.expected` files.  Any difference or
  build failure produces a nonzero exit status.  Additionally, `git diff --
  tests/*.txt` is executed at the end of the run, showing differences for
  those `*.txt` files which were generated.

Only the font regression suite uses the directory `tests/`.  The generated
documents are independently compilable. Their names encode the family option,
zero style and straightquotes flag (`0` or `1`). The two
`generated-direct-*.tex` documents exercise direct NFSS use.  Use `make
generate-font-tests` only to regenerate the test fixtures.  This uses the
installed `ts1enc.def` to enumerate TS1 commands. Review the changes to the
`.tex` and `.expected` files, then run the tests again before committing
updated results, inclusive of the `.txt` files.

## Installation in TEXMFHOME

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

