ifndef config
	config=debug
endif

ifeq ($(config), debug)
	outdir=debug
else
	outdir=release
endif

PAC_NAME=pyrite

ORIGDIR = $(CURDIR)

PYSRC=$(wildcard $(PAC_NAME)/*.py)
PYOUT=$(patsubst $(PAC_NAME)/%.py, $(outdir)/$(PAC_NAME)/%.py, $(PYSRC))

UISRC=$(wildcard ui/*.ui)
UIOUT=$(patsubst ui/%.ui, $(outdir)/$(PAC_NAME)/%.py, $(UISRC))
PYUIC=pyside-uic

all: packagedir copydeps $(PYOUT) $(UIOUT)

run: all
	cp Pyrite.py debug/
	cd debug; python Pyrite.py

test: testunit testinteg testui testend2end

dist: distmac distwin

distmac: FORCE
	mkdir -p dist
	make config=release
	python setup.py bdist_esky
	rm *.pyc

distwin: FORCE
	mkdir -p dist
	make config=release
	/Applications/VMware\ Fusion.app/Contents/Library/vmrun -gu "$(WINDOWS_GUEST_USER)" -gp "$(WINDOWS_GUEST_PWORD)" start "$(WINDOWS_GUEST_FILE)"
	/Applications/VMware\ Fusion.app/Contents/Library/vmrun -gu "$(WINDOWS_GUEST_USER)" -gp "$(WINDOWS_GUEST_PWORD)" copyFileFromHostToGuest "$(WINDOWS_GUEST_FILE)" "build_update_$(PAC_NAME).bat" "C:\\build_update_$(PAC_NAME).bat"
	/Applications/VMware\ Fusion.app/Contents/Library/vmrun -gu "$(WINDOWS_GUEST_USER)" -gp "$(WINDOWS_GUEST_PWORD)" runProgramInGuest "$(WINDOWS_GUEST_FILE)" -interactive "C:\windows\system32\cmd.exe" "/C C:\build_update_$(PAC_NAME).bat"
	rm -f *.pyc

push: pushmac pushwin

pushwin: FORCE
ifdef version
	scp -P 1337 dist/Pyrite-$(version).win32.zip craigjb@10.78.55.224:/var/www/pyrite/downloads/
endif

pushmac: FORCE
ifdef version
	scp -P 1337 dist/Pyrite-$(version).macosx-10_8-x86_64.zip craigjb@10.78.55.224:/var/www/pyrite/downloads/
endif

testunit: all
	export PYTHONPATH=$(ORIGDIR)/$(outdir);cd test/unit;nosetests
	rm -rf test/unit/*.pyc

testinteg: all
	export PYTHONPATH=$(ORIGDIR)/$(outdir);cd test/integration;nosetests
	rm -rf test/integration/*.pyc

testui: all
	export PYTHONPATH=$(ORIGDIR)/$(outdir);cd test/ui;nosetests
	rm -rf test/ui/*.pyc

testend2end: all
	export PYTHONPATH=$(ORIGDIR)/$(outdir);cd test/end2end;nosetests
	rm -rf test/end2end/*.pyc

testpart: all
	export PYTHONPATH=$(ORIGDIR)/$(outdir);cd $(testdir);nosetests $(testfile)

copydeps: malachite
	cp -f version.py $(outdir)/$(PAC_NAME)/
	cp -rf ../malachite/$(outdir)/malachite $(outdir)/$(PAC_NAME)/

malachite: FORCE
	cd ../malachite;make config=$(config)

packagedir:
	mkdir -p $(outdir)/$(PAC_NAME)

$(outdir)/$(PAC_NAME)/%.py : $(PAC_NAME)/%.py
	cp -f $? $@

$(outdir)/$(PAC_NAME)/%.py : ui/%.ui
	$(PYUIC) -o $@ $?
	cp -rf ui/assets $(outdir)/$(PAC_NAME)/
	touch $(outdir)/$(PAC_NAME)/assets/__init__.py

clean: FORCE
	rm -rf debug
	rm -rf release
	rm -rf dist
	rm -rf build

FORCE:

