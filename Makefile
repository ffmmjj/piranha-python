.PHONY: test, build

venv: venv/touchfile

venv/touchfile: requirements.txt
	test -d venv || virtualenv venv
	. venv/bin/activate; pip install -Ur requirements.txt
	touch venv/touchfile

test: venv
	. venv/bin/activate; PYTHONPATH='./src' python -m unittest

build:
	. venv/bin/activate; python3 -m build

release-test:
	. venv/bin/activate; python3 -m twine upload --repository testpypi dist/*