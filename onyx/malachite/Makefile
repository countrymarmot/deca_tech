ifndef config
	config=debug
endif

ifeq ($(config), debug)
	outdir=debug
else
	outdir=release
endif

ORIGDIR = $(CURDIR)

PYSRC=$(wildcard malachite/*.py)
PYOUT=$(patsubst malachite/%.py, $(outdir)/malachite/%.py, $(PYSRC))

all: packagedir $(PYOUT) protocols

test: all
ifdef pdb
	export PYTHONPATH=$(ORIGDIR)/$(outdir);cd test;nosetests --pdb
else
	export PYTHONPATH=$(ORIGDIR)/$(outdir);cd test;nosetests --with-cov --cov malachite $(COV)
endif
	rm -f test/*.pyc

packagedir:
	mkdir -p $(outdir)/malachite

$(outdir)/malachite/%.py : malachite/%.py
	cp -f $? $@

protocols:
	protoc --python_out=$(outdir)/malachite --proto_path=../zinc/protocols ../zinc/protocols/zinc.proto

clean: FORCE
	rm -rf debug
	rm -rf release

FORCE:

