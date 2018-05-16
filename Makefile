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
	rm -rf duden/__pycache__ tests/__pycache__

localization:
	./duden/locale/build.sh

package: localization
	python setup.py sdist
