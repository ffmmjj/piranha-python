.PHONY: test

test:
	poetry run python -m unittest

coverage:
	poetry run coverage run -m unittest

coverage-report: coverage
	poetry run coverage report

coverage-xml: coverage
	poetry run coverage xml

coverage-html: coverage
	poetry run coverage html

build:
	poetry build

release-test: build
	poetry run twine upload --repository testpypi dist/*
