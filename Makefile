PYTHON ?= python3

PYCOVERAGE := $(PYTHON) -m coverage

all: pycheck coverage

test:
	$(PYCOVERAGE) run --source codegen tests/autotest.py

pycheck:
	scripts/pycheck.sh

coverage: test
	$(PYCOVERAGE) report -m | grep -v __init__
