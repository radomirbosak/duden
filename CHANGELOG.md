# Changelog

## Unreleased

## 0.19.1 (2024-02-27)

Other:

* Revive the removed grammar-related CLI options and word properties just to gracefully redirect the user to use the replacement, `--inflect` and `.inflection`

## 0.19.0 (2024-02-25)

Breaking:

* Rework and fix (grammatic) inflection parsing
  * Replace the `.grammar` and `.grammar_raw` word properties with `.inflection`, `--grammar` with `--inflect`

New features:

* Add `pronunciation_audio_url` property #183 by @mundanevision20
* Synonyms are now properly split #195

Bugfixes:

* Fix failing "words_before" and "words_after" properties #191

## 0.18.0 (2022-09-21)

New features:

* Add 10 second timeout to every network request to prevent program hanging #164
* Display word origin in the standard CLI word output #168
* Add new word attribute `DudenWord.grammar_overview` or `--grammar-overview` #168

```console
$ duden Barmherzigkeit --grammar-overview
die Barmherzigkeit; Genitiv: der Barmherzigkeit
```

Intenal:

* Change dependency management tool from pipenv to poetry #160

Documentation:

* Document localization process #167
* Document word origin property #168

## 0.17.0 (2022-09-16)

Breaking:

* Drop python 3.3 compatibility (due to use of `pathlib`)

Other:

* Add pretty project page in pypi via `long_description` setup.py attribute #159 by @mundanevision20

## 0.16.1 (2022-09-14)

New features:

* Use `https` instead of `http` #157 by @mundanevision20

Internal:

* Remove grammar from test data #155

Known bugs:

* Grammar data is not parsed #156

## 0.16.0 (2021-10-11)

New features:

* Add "alternative_spellings" property #147 by @VIEWVIEWVIEW

Bugfixes:

* Fix name, article properties and export for certain words with alternate spellings #147 by @VIEWVIEWVIEW

## 0.15.0 (2021-10-04)

New features:

* Display word's IPA pronunciation #136 by @VIEWVIEWVIEW

## 0.14.4 (2021-05-02)

Bugfix release.

Bugfixes:

* Duden not working for python 3.7 and older #132 (thanks @Dvev for reporting)

## 0.14.3 (2021-04-19)

New features:

* Function to get word of the day `duden.get_word_of_the_day` #129 thanks to @MiVHQW

Bugfixes:

* Reload word when cache is corrupt #131

## 0.14.2 (2021-04-11)

Bugfix release.

Bugfixes:

* Fix cache dir creation on Windows #128
* Fix displaying words with missing grammar #125

## 0.14.1 (2021-02-27)

Bugfix release.

Bugfixes:

* Handle words without grammar information #120
* Fix name and article attributes for non-nouns #119 #121

## 0.14.0 (2020-08-05)

New features:

* Add option to list words before and after `--words-before`, `--words-after`
* Make export (`--export`) more deterministic with alphabetical sorting

Bugfixes:

* Fix utf-8 encoding error on Windows (thanks to @anetschka)
* Add missing dependency on pyyaml (thanks to @mnaberez)
* Fix `-V` not printing the program version
* Fix exporting for words with no grammar data
* Remove extra newline in export output

Internal:

* Test data fix due to upstream dictionary data change

## 0.13.0 (2020-06-14)

New features:

* Speed improvements with caching (`--no-cache`) #83
* Enable exporting data in yaml format (`--export`) #92

Bugfixes:

* Fix grammar table for verbs (`--grammar`) #94

Internal:

* Split up the main module into more smaller ones #98
* Improve documentation #38
* Make code pylint-compatible #97

## 0.12.2 (2020-05-24)

Bugfixes:

* Removed figure annotations from meaning overview

## 0.12.1 (2020-05-23)

Bugfixes:

* Adapted code to new duden.de page layout.

Features:

* Added bash and fish shell completion

## 0.11.2 (2018-08-24)

New features

* colorized output by @Scriptim
* Esperanto localization by @jorgesumle

Bug fixes

* locale files made more consistent by @Scriptim

## 0.11.1 (2018-08-03)

The version 0.11.1 brings many bugfixes, german and spanish UI translation, CLI improvements, and ability to search (multiple) words.

Special thanks goes to @Scriptim and @jorgesumle for contributing.

## 0.10.0 (2017-04-01)

Documentation:

* Document usage

## 0.9.0 (2017-04-01)

First version released to [PyPI](https://pypi.org/project/duden/).

* Improve README
* Add docstrings
* Bugfixes
* Turn duden into package
* Add flake8, autopep8
* Add travis CI

## First commit (2015-10-22)

Add simple script to print

* meaning overview
* synonyms
* meanings
* words before and after
* correct writing

of a German word given as an commandline argument.
