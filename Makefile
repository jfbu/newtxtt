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
