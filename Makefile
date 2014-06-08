PY_PLATFORM=$(shell python -c 'import distutils.util;print distutils.util.get_platform()')
PY_VERSION=$(shell python -c 'import sys;print "%i.%i" % sys.version_info[:2]')
LIB=build/lib.$(PY_PLATFORM)-$(PY_VERSION)
PYTHON=PYTHONPATH=$(LIB) python
FULLNAME=$(shell python setup.py --fullname)

.PHONY: build test docs sdist deb

build:
	python setup.py build

test: build
	$(PYTHON)2.7 $(LIB)/pattern/__init__.py
	$(PYTHON)3 $(LIB)/pattern/__init__.py

README.rst:
	$(PYTHON) -c 'import pattern;print pattern.__doc__' > README.rst

docs: README.rst

sdist: $(FULLNAME).tar.gz

$(FULLNAME).tar.gz: build
	python setup.py sdist

deb: $(FULLNAME).tar.gz
	cd dist; tar -xf $(FULLNAME).tar.gz; cd $(FULLNAME); debuild -i -uc -us