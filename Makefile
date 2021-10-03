.PHONY: all test check testloop clean localization package

all: test check

test:
	python --version
	python -m pytest tests/

check:
	autopep8 --max-line-length 99  --diff -r duden/ tests/ | colordiff
	flake8 --builtins="_" --max-line-length 99 duden/ tests/
	pylint --disable consider-using-f-string duden/ tests/*.py  --good-names 'f,i'

testloop:
	while inotifywait -q -r -e modify --exclude .git .; do \
		clear; make; \
	done

clean:
	rm -rf duden/__pycache__ tests/__pycache__ dist/ duden.egg-info/ build/

localization:
	./duden/locale/build.sh

package: localization
	python3 setup.py sdist bdist_wheel

pypi-upload-test:
	python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

pypi-upload:
	python3 -m twine upload dist/*

completions-install-bash:
	cp completions/duden /etc/bash_completion.d/ || echo "You may need to use sudo to copy to /etc/bash_completion.d"

completions-install-fish:
	cp completions/duden.fish ~/.config/fish/completions/

update-test-data:
	./run_duden.py --export Barmherzigkeit > tests/test_data/Barmherzigkeit.yaml
	./run_duden.py --export Feiertag > tests/test_data/Feiertag.yaml
	./run_duden.py --export laufen > tests/test_data/laufen.yaml
	./run_duden.py --export Qat > tests/test_data/Qat.yaml
	./run_duden.py --export Kragen > tests/test_data/Kragen.yaml
	./run_duden.py --export Petersilie > tests/test_data/Petersilie.yaml
	./run_duden.py --export einfach -r1 > tests/test_data/einfach.yaml
