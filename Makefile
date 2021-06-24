.PHONY: test

test:
	PYTHONPATH='./piranha_python' poetry run python -m unittest

build:
	poetry build

release-test: build
	poetry publish -r testpypi
