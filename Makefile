SHELL := /bin/bash
sourcefiles := $(shell find newtxtt -type f)

.PHONY: doc ctan checkfiles cleanbuild test original

checkfiles:
	@hidden=$$(find newtxtt -name '.*' -print); \
	if [ -n "$$hidden" ]; then \
	    echo -e "Unexpected hidden entries:\n$$hidden\n" >&2; \
	    exit 1; \
	fi
	@find newtxtt -type f | LC_ALL=C sort | diff -u tools/file-list.txt -

original:
	mkdir -p original
	unzip -o newtxtt-1.059-2024-03-12.zip -d original

ctan: checkfiles test $(sourcefiles) ctanbuild/privacy.sh ctanbuild/dopdfdoc.sh
	@echo 'Removing CTAN/newtxtt.zip if it exists (or not...).'
	rm -fr CTAN/newtxtt.zip
	@echo 'Removing all of ctanbuild/newtxtt'
	rm -fr ctanbuild/newtxtt
	rm -f  ctanbuild/newtxtt.zip
	cp -ar newtxtt ctanbuild/
	@echo '********'
	@echo 'Producing the PDF after having un-obfuscated this this person name'
	cd ctanbuild && ./privacy.sh && ./dopdfdoc.sh
	@echo '********'
	@echo 'removing all LaTeX build left-overs'
	mv ctanbuild/newtxtt/doc/newtxtt-doc.{tex,pdf,fls} ctanbuild/
	rm -f ctanbuild/newtxtt/doc/newtxtt-doc.*
	cd ctanbuild && mv newtxtt-doc.{tex,pdf} newtxtt/doc/
	find ctanbuild/newtxtt -type d -exec chmod a+rx {} +
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
	@echo 'Prepare the CTAN announcement, if any.'
	@echo 'Execute .gettimestamps.sh to store the time-stamps,'
	@echo 'then commit the current repertory state with the'
	@echo 'announcement as commit message.'
	@echo 'The next instructions are ONLY for the original creator'
	@echo 'of the provisory github repository: They do not apply'
	@echo 'to people having cloned this repo to their own namespace;'
	@echo '==== DO NOT COMMIT THE ctanbuild/newtxtt.zip.'
	@echo '==== Create a branch which will be kept private'
	@echo '==== and never pushed to GitHub.'
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
