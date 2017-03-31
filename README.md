# Duden down [![Build Status](https://travis-ci.org/radomirbosak/duden-down.svg?branch=master)](https://travis-ci.org/radomirbosak/duden-down)

_dudendown_ is a CLI-based program, which prints out the information about a given german word. The printed data are parsed from german site [duden.de](duden.de).

The program uses `beautifulsoup` package to parse and traverse the HTML structure.

## Installation
```console
pip install dudendown
```

## Usage

### CLI
```console
$ duden Loeffel
Löffel, der
===========
Word type: Substantiv, maskulin
Commonness: 2/5
Separation: Löf|fel
Meaning overview:
 0.  a. [metallenes] [Ess]gerät, an dessen unterem Stielende eine schalenartige Vertiefung sitzt und das zur Aufnahme von Suppe, Flüssigkeiten, zur Zubereitung von Speisen o. Ä. verwendet wird
     b. (Medizin) Kürette

 1. (Jägersprache) Ohr von Hase und Kaninchen

Synonyms:
Ohr; [Ge]hörorgan; (salopp) Horcher, Horchlappen, Lauscher; (Jägersprache) Loser, Teller
```

### Module usage

```python
>>> import duden
>>> w = duden.get('Loeffel')
>>> w.word_separation
['Löf', 'fel']
>>> w.synonyms
'Ohr; [Ge]hörorgan; (salopp) Horcher, Horchlappen, Lauscher; (Jägersprache) Loser, Teller'
```

## Dependencies

Python modules:
* beautifulsoup4
* requests

## Testing

```console
make test
```