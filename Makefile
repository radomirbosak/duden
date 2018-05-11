all:
	@echo "Available:"
	@echo "make test"
	@echo "make testloop"

test:
	python --version
	python -m pytest tests/
	autopep8 --diff -r duden/ | colordiff
	autopep8 --diff -r tests/ | colordiff
	flake8 duden/ tests/

testloop:
	while inotifywait -q -r -e modify --exclude .git .; do \
		clear; make test; \
	done

clean:
	rm -rf duden/__pycache__ tests/__pycache__
