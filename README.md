Duden down
==========

_dudendown_ is a CLI-based program, which prints out the information about a given german word. The printed data are parsed from german site [duden.de](duden.de).

The program uses `BeautifulSoup` package to parse and traverse the HTML structure.

![Screenshot](screenshot.png)

Usage
-----
```console
python3 duden/duden.py Loeffel
```

Dependencies
------------
Python modules:
* beautifulsoup4
* requests

Testing
-------

```console
make test
```