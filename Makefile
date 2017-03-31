all:
	@echo "Available:"
	@echo "make test"
	@echo "make testloop"

test:
	green tests/ --quiet-stdout
	autopep8 --diff -r . | colordiff
	autopep8 --diff -r tests/ | colordiff
	flake8 shellcut/ tests/ setup.py

testloop:
	while inotifywait -q -r -e modify --exclude .git .; do \
		clear; make test; \
	done
