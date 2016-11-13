Duden down
==========

dudendown is a CLI-based program, which prints out the information about a given german word. The printed data are parsed from german site [duden.de](duden.de).

The program uses `BeautifulSoup` package to parse and traverse the HTML structure.

![Screenshot](screenshot.png)

Usage
-----
	python3 duden.py Loeffel


Dependencies
------------
Python modules:
* beautifulsoup4
* requests

To install them on Fedora, run:
```
dnf install python3-requests python3-beautifulsoup4
```


Contributing
------------
The code (in the most recent commit) of `master` and `develop` branches should
* pass the unit tests
* pass the pep8 check (see further sections).
* be functional and usable by user (master) or developer (develop)

Code in other branches can be broken/non-functional/not-adhering to standards.

Non-hotfix changes should be first merged to develop branch; multiple develop branch changes can then be merged to master.


Unit Testing
------------
    python3 -m unittest discover tests/ -v


Pep8 code quality check
-----------------------
    python3-autopep8 -r . --diff

Note that this command requires the autopep8 python module. In Fedora 24 it can be installed by:

```
dnf info python3-autopep8
```
