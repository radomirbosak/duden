Duden down
==========

dudendown is a CLI-based program, which prints out the meaning of given german word. The printed data are parsed from german site [duden.de](duden.de).

The program uses `BeautifulSoup` package to parse and traverse the HTML structure.

![Screenshot](screenshot.png)

Usage
-----
	python3 dudendown.py Loeffel


Unit Testing
------------
    python3 -m unittest discover tests/ -v