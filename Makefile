.PHONY: all test testloop clean localization package

all:
	@echo "Available:"
	@echo "make test"
	@echo "make testloop"

test:
	python --version
	python -m pytest tests/
	autopep8 --diff -r duden/ | colordiff
	autopep8 --diff -r tests/ | colordiff
	flake8 --builtins="_" duden/

testloop:
	while inotifywait -q -r -e modify --exclude .git .; do \
		clear; make test; \
	done

clean:
	rm -rf duden/__pycache__ tests/__pycache__ dist/ duden.egg-info/ build/

localization:
	./duden/locale/build.sh

package: localization
	python setup.py sdist bdist_wheel

pypi-upload-test:
	python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

pypi-upload:
	python3 -m twine upload dist/*

completions-install-bash:
	cp completions/duden /etc/bash_completion.d/ || echo "You may need to use sudo to copy to /etc/bash_completion.d"

completions-install-fish:
	cp completions/duden.fish ~/.config/fish/completions/
