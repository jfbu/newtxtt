SHELL := /bin/bash
sourcefiles := $(shell find newtxtt -type f)

.PHONY: pdfdoc ctan checkfiles cleanaux cleanbuild test original

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

ctan: test $(sourcefiles) pdfdoc checkhiddenfiles
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
	@echo 'Checking the list of archived files for omiisions or additions... '
	@unzip -Z1 CTAN/newtxtt.zip | sed '/\/$$/d' | LC_ALL=C sort | diff -u tools/file-list.txt -
	@echo '... ok'
	@echo 'Checking archive integrity...'
	unzip -tq CTAN/newtxtt.zip
	@echo '... ok'
	@echo '********'
	@echo 'CHECK ctanbuild/newtxtt-doc.fls FOR ANY INCONGRUITY.'
	@echo 'Copy the newtxttt.zip to some other place for CTAN upload.'
	@echo 'Rename the one in CTAN to hold the version number in its filename.'
	@echo 'Prepare the CTAN announcement, if any.'
	@echo 'Execute .gettimestamps.sh to store the time-stamps,'
	@echo 'then commit the current repository state with the'
	@echo 'announcement as commit message body.'
	@echo '********'

test:
	@echo '********'
	@echo 'Running regression tests (use make original first if needed)...'
	python3 tools/audit-ts1.py
	python3 tools/audit-distribution.py --reference original/newtxtt
	python3 tools/test-latex.py
	@echo '... done'
	@echo '********'

cleanbuild:
	rm -fr ctanbuild/newtxtt

# Build a TDS archive from the already validated CTAN archive.
# set -eu: stop on command failure or expansion of an unset variable.
# mktemp -d: create a fresh temporary directory.
# trap ... EXIT: remove that temporary tree on shell exit, even on failure
# (rm -rf: recursive removal without prompting).
# unzip -q -d: extract quietly into the specified directory.
# mkdir -p: create parent directories as needed.
# zip -X -r: omit extra file attributes and archive directories recursively.
# unzip -tq: test archive integrity quietly before moving it into place.
CTAN/newtxtt.tds.zip: CTAN/newtxtt.zip
	set -eu; \
	tmp=$$(mktemp -d); \
	trap 'rm -rf "$$tmp"' EXIT; \
	unzip -q "$<" -d "$$tmp"; \
	cd "$$tmp"; \
	mkdir -p tex/latex doc/fonts \
	    fonts/tfm/public fonts/type1/public \
	    fonts/enc/dvips fonts/map/dvips; \
	mv newtxtt/tex tex/latex/newtxtt; \
	mv newtxtt/doc doc/fonts/newtxtt; \
	mv newtxtt/tfm fonts/tfm/public/newtxtt; \
	mv newtxtt/type1 fonts/type1/public/newtxtt; \
	mv newtxtt/enc fonts/enc/dvips/newtxtt; \
	mv newtxtt/map fonts/map/dvips/newtxtt; \
	mv newtxtt/README doc/fonts/newtxtt/; \
	rmdir newtxtt; \
	zip -X -r newtxtt.tds.zip doc tex fonts; \
	unzip -tq newtxtt.tds.zip; \
	mv newtxtt.tds.zip "$(abspath $@)"
