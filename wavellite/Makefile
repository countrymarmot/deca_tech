ifndef config
	config=debug
endif

ifeq ($(config), debug)
	outdir=debug
else
	outdir=release
endif

PAC_NAME=wavellite

ORIGDIR=$(CURDIR)

PYSRC=$(wildcard $(PAC_NAME)/*.py)
PYOUT=$(patsubst $(PAC_NAME)/%.py, $(outdir)/$(PAC_NAME)/%.py, $(PYSRC))

UISRC=$(wildcard ui/*.ui)
UIOUT=$(patsubst ui/%.ui, $(outdir)/$(PAC_NAME)/%.py, $(UISRC))
PYUIC=pyside-uic

all: packagedir copydeps $(PYOUT) $(UIOUT)

run: all
	cd $(outdir)/$(PAC_NAME); python $(PAC_NAME).py

dist: distmac distwin

distmac: FORCE
	make config=release
	python setup.py bdist_esky
	rm -f *.pyc

distwin: FORCE
	make config=release
	# copy the bat file for building the update over and run it
	/Applications/VMware\ Fusion.app/Contents/Library/vmrun -gu "$(WINDOWS_GUEST_USER)" -gp "$(WINDOWS_GUEST_PWORD)" start "$(WINDOWS_GUEST_FILE)"
	/Applications/VMware\ Fusion.app/Contents/Library/vmrun -gu "$(WINDOWS_GUEST_USER)" -gp "$(WINDOWS_GUEST_PWORD)" copyFileFromHostToGuest "$(WINDOWS_GUEST_FILE)" "build_update_$(PAC_NAME).bat" "C:\\build_update_$(PAC_NAME).bat"
	/Applications/VMware\ Fusion.app/Contents/Library/vmrun -gu "$(WINDOWS_GUEST_USER)" -gp "$(WINDOWS_GUEST_PWORD)" runProgramInGuest "$(WINDOWS_GUEST_FILE)" -interactive "C:\windows\system32\cmd.exe" "/C C:\build_update_$(PAC_NAME).bat"
	rm -f *.pyc

push: pushmac pushwin

pushwin: FORCE
ifdef version
	scp -P 1337 dist/Wavellite-$(version).win32.zip craigjb@10.78.55.224:/var/www/wavellite/downloads/
endif

pushmac: FORCE
ifdef version
	scp -P 1337 dist/Wavellite-$(version).macosx-10_8-x86_64.zip craigjb@10.78.55.224:/var/www/wavellite/downloads/
endif

copydeps:
	cp -f version.py $(outdir)/$(PAC_NAME)/

packagedir:
	mkdir -p $(outdir)/$(PAC_NAME)

$(outdir)/$(PAC_NAME)/%.py : $(PAC_NAME)/%.py
	cp -f $? $@

$(outdir)/$(PAC_NAME)/%.py : ui/%.ui
	$(PYUIC) -o $@ $?
	cp -rf ui/assets $(outdir)/$(PAC_NAME)/
	touch $(outdir)/$(PAC_NAME)/assets/__init__.py

clean: FORCE
	rm -rf debug/*
	rm -rf release/*
	rm -rf dist/*
	rm -rf build

FORCE:

