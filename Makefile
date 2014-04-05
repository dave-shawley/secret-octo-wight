TARGET_PYTHON = python3.3
TARGET_TOX = py33
DOWNLOAD ?= curl -sL
PIP_LOCATION = https://raw.github.com/pypa/pip/master/contrib/get-pip.py

BUILDDIR = build
COVERAGE = $(ENVDIR)/bin/coverage
DISTDIR ?= dist
ENVDIR = env
FIND ?= find
PIP = $(ENVDIR)/bin/pip
PYTHON = $(ENVDIR)/bin/python
REPORTDIR = reports
RM ?= rm -f
RMDIR ?= rm -fr
STATEDIR = .state
TOX = $(ENVDIR)/bin/tox


export NOSE_COVER_TEXT=no

#
# Testing Targets
#
.PHONY: test coverage

test: environment
	$(PYTHON) setup.py test

coverage:
	@- $(RM) -r $(REPORTDIR)/coverage
	$(PYTHON) setup.py test --environment $(TARGET_TOX) --with-coverage
	$(COVERAGE) html '--omit=$(ENVDIR)/*' --directory=$(REPORTDIR)/coverage

#
# Development Environment Targets
#
.PHONY: environment

environment: $(STATEDIR) $(STATEDIR)/virtualenv $(STATEDIR)/requirements-installed

$(STATEDIR)/virtualenv:
	virtualenv --python=$(TARGET_PYTHON) --prompt='{family-tree}' --no-setuptools --no-pip $(ENVDIR)
	$(DOWNLOAD) "$(PIP_LOCATION)" | $(ENVDIR)/bin/python
	touch "$@"

$(STATEDIR)/requirements-installed: $(STATEDIR)/requirements.txt
	$(PIP) install -r "$<"
	touch "$@"

$(STATEDIR)/requirements.txt: $(wildcard requirements/*.txt)
	cat $^ > "$@"

$(STATEDIR) $(DISTDIR):
	@- test -d "$@" || mkdir -p "$@"

#
# Housekeeping Targets
#
.PHONY: clean dist-clean maintainer-clean

clean:
	- $(RM) .coverage
	- $(FIND) . -name '*.pyc' -delete
	- $(FIND) . -name '__pycache__' -delete

dist-clean: clean
	- $(RMDIR) $(BUILDDIR) $(REPORTDIR) $(DISTDIR) *.egg-info
	- $(RM) *.egg

maintainer-clean: dist-clean
	- $(RMDIR) $(STATEDIR) $(ENVDIR)

#
# Distribution Targets
#
.PHONY: docs sdist

docs: environment
	@- $(FIND) $(BUILDDIR)/doc -name '*.doctree' -delete
	$(PYTHON) setup.py build_sphinx

sdist: test
	$(PYTHON) setup.py sdist

