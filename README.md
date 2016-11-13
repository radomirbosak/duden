Duden down
==========

dudendown is a CLI-based program, which prints out the about a given german word. The printed data are parsed from german site [duden.de](duden.de).

The program uses `BeautifulSoup` package to parse and traverse the HTML structure.

![Screenshot](screenshot.png)

Usage
-----
	python3 duden.py Loeffel


Unit Testing
------------
    python3 -m unittest discover tests/ -v

Dependencies
------------
Python modules:
* beautifulsoup4
* requests

To install them on Fedora, run:
```
dnf install python3-requests python3-beautifulsoup4
```