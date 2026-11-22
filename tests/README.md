# Font regression tests

From the repository root, run `make test-font-regression` to compile
and verify the checked-in tests. The `.tex` sources and `.expected` files
are not regenerated. The `.txt` files record the observed PDF glyphs and,
where checked, Unicode text. Compilation and assertion failures produce a
nonzero exit status and are recorded in the corresponding `.txt` file.
Use `git diff -- tests/` to examine changes in the results.

Run `make generate-font-tests` only when intentionally
regenerating the test fixtures. This uses the installed `ts1enc.def` to
enumerate TS1 commands. Review the changes to the `.tex` and `.expected`
files, then run the tests again before committing updated results.

The generated documents are independently compilable. Their names encode
the family option, zero style and straightquotes flag (`0` or `1`). The
two `generated-direct-*.tex` documents exercise direct NFSS use.
