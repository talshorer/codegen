PYTHON := python3

export PYTHONPATH := $(PWD)/..

test:
	$(PYTHON) -m unittest discover -s tests -v
