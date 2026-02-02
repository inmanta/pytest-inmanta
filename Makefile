# Shortcuts for various dev tasks. Based on makefile from pydantic
.DEFAULT_GOAL := all
isort = isort pytest_inmanta tests examples
black = black pytest_inmanta tests examples
flake8 = flake8 pytest_inmanta tests examples

.PHONY: install
install:
	pip install -U --upgrade-strategy=eager pip setuptools wheel
	pip install -U --upgrade-strategy=eager -e . -c requirements.txt -r requirements.dev.txt

.PHONY: format
format:
	$(isort)
	$(black)
	$(flake8)

.PHONY: pep8
pep8:
	$(flake8)

RUN_MYPY=python -m mypy --html-report mypy -p pytest_inmanta
mypy_baseline = python -m mypy_baseline

.PHONY: mypy ci-mypy
mypy:
	$(RUN_MYPY) | $(mypy_baseline) filter --sort-baseline
ci-mypy:
	$(RUN_MYPY) --junit-xml junit-mypy.xml --cobertura-xml-report coverage | $(mypy_baseline) filter --no-colors --sort-baseline

.PHONY: mypy-sync
mypy-sync:
	$(RUN_MYPY) | $(mypy_baseline) sync --sort-baseline

.PHONY: test
test:
	pytest -vvv --log-level DEBUG tests

.PHONY: all
all: pep8 test mypy

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf mypy
	rm -rf coverage
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
	find -name .env | xargs rm -rf
	python setup.py clean
