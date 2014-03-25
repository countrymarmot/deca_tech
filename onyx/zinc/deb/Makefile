# This makefile will only run on Debian Linux systems.
# It is meant to generate a .deb package for installation
# onto Debian and Ubuntu systems.

all: package

clean:
	rm -rf ./zinc
	rm -f zinc.deb

package: directories binary control
	dpkg-deb --build zinc

control: directories
	cp ./control ./zinc/DEBIAN/control

directories:
	mkdir -p ./zinc/usr/bin
	mkdir -p ./zinc/DEBIAN

binary:
	cp ../release/zinc ./zinc/usr/bin/zinc

.FORCE:
