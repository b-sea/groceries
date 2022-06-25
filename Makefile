.PHONY: venv requirements docs

## Dev Workflow
venv:
	@${PYTHON3} -m venv venv

clean-venv:
	@rm -rf ./venv

setup:
	@pip3 install pip-tools
	@pip-sync requirements/dev.txt && \
	pip3 install -e .
	@#pre-commit install -c ./.githooks/.pre-commit-config.yml

freeze:
	@pip-compile requirements/docs.in
	@pip-compile requirements/test.in
	@pip-compile requirements/dev.in

coverage: clean-coverage
	@coverage run --rcfile=setup.cfg -m unittest discover -v
	@coverage html
	@xdg-open htmlcov/index.html

clean-coverage:
	@rm -rf .coverage
	@rm -rf ./htmlcov

test:
	@python3 -m unittest discover -v

tox: clean-tox
	tox -c ./setup.cfg

clean-tox:
	@rm -rf ./.tox

docs: clean-docs
	@sphinx-build -E -a -b html ./docs ./build/docs
#	@xdg-open ./build/docs/index.html
	@start "./build/docs/index.html"

clean-docs:
	@rm -rf ./docs/_build

lint:
	@pylint --rcfile=setup.cfg src/cs_ftrack_events

clean-build:
	@rm -rf ./build
	@rm -rf ./dist

build:
	@python3 -m build --wheel

clean: clean-coverage clean-docs clean-tox clean-build

clean-all: clean clean-venv
	@rm -rf ./src/*.egg-info
