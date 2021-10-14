# Usage

This example showcases the most useful functions of the `DudenWord` class.

## Word functions and properties

```python
> import duden
> w = duden.get('Barmherzigkeit')

> w.title
'Barmherzigkeit, die'

> w.name
'Barmherzigkeit'

> w.urlname  # word identifier in url
'Barmherzigkeit'

> w.article
'die'

> w.part_of_speech
'Substantiv, feminin'

> w.frequency  # of 5
2

> w.usage
'gehoben'

> w.word_separation
['Barm', 'her', 'zig', 'keit']

> w.meaning_overview
'barmherziges Wesen, Verhalten'

> w.synonyms
'[Engels]güte, Milde, Nachsicht, Nachsichtigkeit; (gehoben) Herzensgüte, Mildtätigkeit, Seelengüte; (bildungssprachlich) Humanität, Indulgenz; (veraltend) Wohltätigkeit; (Religion) Gnade'

> w.origin
'mittelhochdeutsch barmherzekeit, barmherze, althochdeutsch armherzi, nach (kirchen)lateinisch misericordia'

> w = duden.get('laufen')
> w.compounds
{
  "adjektive": ["schief", "dumm", "glatt", "optimal", "parallel", "rot", "reibungslos", "gut"],
  "substantive": ["Ruder", "Amok", "Vorbereitung", "Gefahr", "Geschäft", "Vertrag", "Hochtour"]
}

> w.grammar_raw
[({'Indikativ', 'Person I', 'Präsens', 'Singular'}, 'ich laufe'),
 ({'Konjunktiv I', 'Person I', 'Präsens', 'Singular'}, 'ich laufe'),
 ({'Imperativ', 'Person I', 'Präsens', 'Singular'}, '–'),
 ({'Indikativ', 'Person II', 'Präsens', 'Singular'}, 'du läufst'),
...
 ({'Konjunktiv II', 'Person III', 'Plural', 'Präteritum'}, 'sie liefen'),
 ({'Partizip I'}, 'laufend'),
 ({'Partizip II'}, 'gelaufen'),
 ({'Infinitiv mit zu'}, 'zu laufen')]

> w.grammar(duden.SINGULAR, duden.PRASENS, duden.INDIKATIV)
['ich laufe', 'du läufst', 'er/sie/es läuft']

> w = duden.get('Meme')
> w.alternative_spellings
['Mem']
```

## Other functions

### get

The `duden.get` function requests directly the url `https://www.duden.de/rechtschreibung/{word}`, and retrieves a single parsed word. If the page was not found, returns `None`.

### search

Some words such as `einfach` have multiple entries in the database and simply fetching `https://www.duden.de/rechtschreibung/einfach` yields a 404 page not found:
```python
> duden.get('einfach')
None
```

For these words, the **search** function should be used.
The `duden.search` function requests the url `https://www.duden.de/suchen/dudenonline/{word}`, and returns a list of search results: which is, by default, a list of parsed words.

```python
> duden.search('einfach')
[einfach (Adjektiv), einfach (Partikel)]

> word1, word2 = duden.search('einfach')
> (word1.name, word1.part_of_speech, word1.urlname)
('einfach', 'Adjektiv', 'einfach_einmal_simpel')

> (word2.name, word2.part_of_speech, word2.urlname)
('einfach', 'Partikel', 'einfach_vollkommen_wirklich')
```

By default, just words with title matching exactly the searched word are returned by the `search` function. To return all results of the `/suchen/dudenonline/` call, use the `exact` keyword:

```python
> duden.search('einfach', exact=False)
[Einfaches (substantiviertes Adjektiv, Neutrum),
 einfach (Adjektiv),
 einfach (Partikel),
...
 Simplum, das (Substantiv, Neutrum)]
```

To avoid automatically retrieving and parsing the search results, use the `return_words` keyword. This will return the word urlnames only.
```python
> duden.search('einfach', return_words=False)
['einfach_einmal_simpel', 'einfach_vollkommen_wirklich']
```

### Word of the day

Retrieves a parses the Word of the day from the main page.
```python
> duden.get_word_of_the_day
Quasimodogeniti (Substantiv ohne Artikel)
```
