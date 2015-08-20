PYTHON ?= python3

PYTHONPATH += $(PWD)/..
export PYTHONPATH

test:
	$(PYTHON) -m unittest discover -s tests -v
