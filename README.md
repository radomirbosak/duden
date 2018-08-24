# Duden [![Build Status](https://travis-ci.org/radomirbosak/duden.svg?branch=master)](https://travis-ci.org/radomirbosak/duden) [![Version](http://img.shields.io/pypi/v/duden.svg?style=flat)](https://pypi.python.org/pypi/duden/)

**duden** is a CLI-based program and python module, which can provide various information about given german word. The provided data are parsed from german dictionary [duden.de](http://duden.de).

![duden screenshot](screenshot.png)

## Installation
```console
pip3 install duden
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
>>> w.name
'Löffel'
>>> w.word_separation
['Löf', 'fel']
>>> w.synonyms
'Ohr; [Ge]hörorgan; (salopp) Horcher, Horchlappen, Lauscher; (Jägersprache) Loser, Teller'
```
For more examples see [usage documentation](docs/usage.md).

## Dependencies

Python modules:
* beautifulsoup4
* requests

## Testing

```console
make test
```

## Supported versions of Python

* Python 3
