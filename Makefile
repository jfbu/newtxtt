SHELL := /bin/bash
sourcefiles := $(shell find newtxtt -type f)

.PHONY: pdfdoc ctan checkfiles cleanaux cleanbuild original
.PHONY: generate-font-tests test-font-regression test-audit test-all

checkhiddenfiles:
	@hidden=$$(find newtxtt -name '.*' -print); \
	if [ -n "$$hidden" ]; then \
	    echo -e "Unexpected hidden entries:\n$$hidden\n" >&2; \
	    exit 1; \
	fi

original:
	rm -fr original
	mkdir -p original
	unzip -o newtxtt-1.059-2024-03-12.zip -d original

pdfdoc:
	@echo '********'
	@echo 'Producing newtxtt-doc.pdf in newtxtt/doc'
	./dopdfdoc.sh

cleanaux:
	rm -f newtxtt/doc/newtxtt-doc.{aux,fdb_latexmk,log,fls}

ctan: test-all $(sourcefiles) pdfdoc checkhiddenfiles
	@echo 'Removing CTAN/newtxtt.zip if it exists (or not...).'
	rm -fr CTAN/newtxtt.zip
	@echo 'Removing all of ctanbuild/newtxtt'
	rm -fr ctanbuild/newtxtt
	rm -f  ctanbuild/newtxtt.zip
	@echo 'Moving all files to ctanbuild/, the PDF doc is done'
	cp -ar newtxtt ctanbuild/
	@echo '********'
	@echo 'removing all LaTeX build left-overs'
	mv ctanbuild/newtxtt/doc/newtxtt-doc.{tex,pdf,fls} ctanbuild/
	rm -f ctanbuild/newtxtt/doc/newtxtt-doc.*
	cd ctanbuild && mv newtxtt-doc.{tex,pdf} newtxtt/doc/
	find ctanbuild/newtxtt -type d -exec chmod a+rx {} +
	@echo '********'
	@echo 'checking the file list is as is recorded as expected'
	cd ctanbuild ; find newtxtt -type f | LC_ALL=C sort | diff -u ../tools/file-list.txt -
	@echo '********'
	@echo 'building the zip'
	umask 0022 && cd ctanbuild && zip -r newtxtt.zip newtxtt
	mv ctanbuild/newtxtt.zip CTAN/
	@echo '********'
	@echo 'New newtxtt.zip now moved to CTAN/ directory.'
	@echo 'Checking the list of archived files for omissions or additions... '
	@unzip -Z1 CTAN/newtxtt.zip | sed '/\/$$/d' | LC_ALL=C sort | diff -u tools/file-list.txt -
	@echo '... ok'
	@echo 'Checking archive integrity...'
	unzip -tq CTAN/newtxtt.zip
	@echo '... ok'
	@echo '********'
	@echo 'CHECK ctanbuild/newtxtt-doc.fls FOR ANY INCONGRUITY.'
	@echo 'Now CTAN holds newtxtt.zip.  Execute'
	@echo '    make CTAN/newtxtt.tds.zip'
	@echo 'if a tds.zip is wished for (useful for local installation)'
	@echo '********'

# Regenerate the font regression test sources and expected glyph data.
# Run only when intentionally updating the test coverage.
generate-font-tests:
	python3 tools/test-font-regression.py --generate

# Audit font files using Python and fontTools, without compiling LaTeX.
# Check consistency between TFM metrics, encoding vectors, Type 1 outlines,
# map entries and FD declarations, and preservation of original font data.
test-audit:
	@echo '********'
	@echo 'Auditing font files (use make original first if needed)...'
	@# tee saves and displays reports; pipefail propagates Python errors.
	@# TS1 coverage against ts1enc.def, metrics, encodings, outlines and maps.
	set -o pipefail; python3 tools/audit-ts1.py | tee tools/ts1-audit.txt
	@# T1/TS1 consistency and FD selections; --reference checks original
	@# metrics, glyph programs, subroutines, font properties and map.
	set -o pipefail; python3 tools/audit-distribution.py --reference original/newtxtt | tee tools/distribution-audit.txt
	@# --exit-code fails if tracked reports differ from the Git index.
	@if ! git diff --exit-code -- tools/ts1-audit.txt tools/distribution-audit.txt; then \
	    echo -e '\033[1;31mERROR: Font audit results have changed.\033[0m' >&2; \
	    exit 1; \
	fi
	@echo '... done'
	@echo '********'

# Compile the checked-in test sources with pdfLaTeX.
# Use Python and pypdf to check PDF font selections, glyph codes and Unicode
# extraction against expected results. Record actual results for comparison
# with Git-controlled baselines; leave sources and expectations unchanged.
test-font-regression:
	@echo '********'
	@echo 'Running font regression tests...'
	python3 tools/test-font-regression.py
	@# --exit-code fails if tracked textual results differ from the Git index.
	@if ! git diff --exit-code -- 'tests/*.txt'; then \
	    echo -e '\033[1;31mERROR: Font regression results have changed.\033[0m' >&2; \
	    exit 1; \
	fi
	@echo '... done'
	@echo '********'

# Run both categories of checks before packaging.
test-all: test-audit test-font-regression

cleanbuild:
	rm -fr ctanbuild/newtxtt

# Build a TDS archive from the already validated CTAN archive.
# rm -rf: remove the previous staging tree recursively, if present.
# unzip -q -d: extract quietly into the specified directory.
# mkdir -p: create parent directories as needed.
# zip -r: archive directories recursively, retaining timestamp metadata.
# unzip -tq: test archive integrity quietly before moving it into place.
CTAN/newtxtt.tds.zip: CTAN/newtxtt.zip
	rm -rf ctanbuild/tds
	mkdir -p ctanbuild/tds
	unzip -q CTAN/newtxtt.zip -d ctanbuild/tds
	mkdir -p ctanbuild/tds/tex/latex
	mkdir -p ctanbuild/tds/doc/fonts
	mkdir -p ctanbuild/tds/fonts/tfm/public
	mkdir -p ctanbuild/tds/fonts/type1/public
	mkdir -p ctanbuild/tds/fonts/enc/dvips
	mkdir -p ctanbuild/tds/fonts/map/dvips
	mv ctanbuild/tds/newtxtt/tex ctanbuild/tds/tex/latex/newtxtt
	mv ctanbuild/tds/newtxtt/doc ctanbuild/tds/doc/fonts/newtxtt
	mv ctanbuild/tds/newtxtt/tfm ctanbuild/tds/fonts/tfm/public/newtxtt
	mv ctanbuild/tds/newtxtt/type1 ctanbuild/tds/fonts/type1/public/newtxtt
	mv ctanbuild/tds/newtxtt/enc ctanbuild/tds/fonts/enc/dvips/newtxtt
	mv ctanbuild/tds/newtxtt/map ctanbuild/tds/fonts/map/dvips/newtxtt
	mv ctanbuild/tds/newtxtt/README ctanbuild/tds/doc/fonts/newtxtt/
	rmdir ctanbuild/tds/newtxtt
	cd ctanbuild/tds && zip -r newtxtt.tds.zip doc tex fonts
	unzip -tq ctanbuild/tds/newtxtt.tds.zip
	mv ctanbuild/tds/newtxtt.tds.zip CTAN/newtxtt.tds.zip
	rm -rf ctanbuild/tds

