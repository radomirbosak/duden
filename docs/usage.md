# Module usage

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
['[Engels]güte', 'Milde', 'Nachsicht', 'Nachsichtigkeit']

> w.origin
'mittelhochdeutsch barmherzekeit, barmherze, althochdeutsch armherzi, nach (kirchen)lateinisch misericordia'

> w.examples
'die Barmherzigkeit Gottes'
'Barmherzigkeit üben'

> w.grammar_overview
'die Barmherzigkeit; Genitiv: der Barmherzigkeit'

> w = duden.get('laufen')
> w.compounds
{
  "adjektive": ["schief", "dumm", "glatt", "optimal", "parallel", "rot", "reibungslos", "gut"],
  "substantive": ["Ruder", "Amok", "Vorbereitung", "Gefahr", "Geschäft", "Vertrag", "Hochtour"]
}

> w.pronunciation_audio_url
'https://.../filename.mp3'

> w.inflection.data
{'Indikativ': {'Präsens': {'ich': 'laufe (mich/mir)',
   'du': 'läufst (dich/dir)',
   'er/sie/es': 'läuft (sich)',
   'wir': 'laufen (uns)',
   'ihr': 'lauft (euch)',
   'sie': 'laufen (sich)'},
 ...
 },
 ...
}

> from duden import Mood, Tense, Person
> w.inflection.verb_conjugate(Mood.INDICATIVE, Tense.PRESENT, Person.FIRST_SINGULAR)
'laufe (mich/mir)'

> w = duden.get('Meme')
> w.alternative_spellings
['Mem']

> w.phonetic
'[mi:m]'
```

## Word inflection

For some nouns, adjectives and verbs, duden provides inflection data. Data structure that provides access to this data is a class called `Inflector` accessible via `word.inflection` attribute.

```python
> word = get("Hase")
> inf = word.inflection
> inf
(Inflector: 'der Hase', ...)
```

This object provides the data in two ways:
1. In raw form `word.inflection.data`:

```python
> inf.data
{'Deklination': {'Singular': {'Nominativ': 'der Hase',
   'Akkusativ': 'den Hasen',
   'Dativ': 'dem Hasen',
   'Genitiv': 'des Hasen'},
  'Plural': {'Nominativ': 'die Hasen',
   'Akkusativ': 'die Hasen',
   'Dativ': 'den Hasen',
   'Genitiv': 'der Hasen'}}}
```

2. Through specific inflection methods like `word.inflection.noun_decline`:
```python
> inf.noun_decline("Singular", "Nominativ")
'der Hase'
```

### Inflection methods
Inflection methods are provided for user's convenience and read data more or less directly from the raw inflection data.

The methods produce an inflected form of the word when given required grammatical categories like _grammatical case_, _person_, _gender_, _tense_ etc.

Grammatical category values can be specified by the following enum values:
```python
> from duden import Number, Case, Gender, Degree, Person, Mood, Tense, ImperativePerson, InfinitiveForm
> Case.NOMINATIVE
<Case.NOMINATIVE: 'Nominativ'>
```

#### Nouns declension
Nouns can be declined by this method:
```python
inf.noun_decline(number, case)
```
where grammatical number and case can attain these values:

| Grammatical category | Values |
| -------------------- | ------ |
| Number | `Number.SINGULAR`, `Number.PLURAL` |
| Case   | `Case.NOMINATIVE`, `Case.GENITIVE`, `Case.DATIVE`, `Case.ACCUSATIVE` |

Example:
```python
> inf = duden.get("Hase").inflection
> inf.noun_decline(Number.PLURAL, Case.DATIVE)
'den Hasen'
```

#### Adjective declension

Adjective declension form is determined by _grammatical gender_ and _case_. Adjective comparison form by _grammatical degree_.

```python
inf.adjective_decline_strong(gender, case)
inf.adjective_decline_weak(gender, case)
inf.adjective_decline_mixed(gender, case)
inf.adjective_compare(degree)
```

| Grammatical category | Values |
| -------------------- | ------ |
| Gender |`Gender.MASCULINE`, `Gender.FEMININE`, `Gender.NEUTER` |
| Case   | `Case.NOMINATIVE`, `Case.GENITIVE`, `Case.DATIVE`, `Case.ACCUSATIVE` |
| Degree | `Degree.POSITIVE`, `Degree.COMPARATIVE`, `Degree.SUPERLATIVE` |

Example:
```python
> inf = duden.get("schnell").inflection
> inf.adjective_compare(Degree.SUPERLATIVE)
'am schnellsten'
```

#### Verb conjugation
Conjugated verb form is determined by the _grammatical mood_, _tense_ and _person_.

The verb imperative and infinitive forms are each defined by only one grammatical category; _person_ (only two values), and _infinitive form_ respectively.

```python
inf.verb_conjugate(mood, tense, person)
inf.verb_imperative(person)
inf.verb_infinitive_forms(form)
```

| Grammatical category | Values |
| -------------------- | ------ |
| Mood | `Mood.INDICATIVE`, `Mood.SUBJUNCTIVE_I`, `Mood.SUBJUNCTIVE_II` |
| Tense | `Tense.PRESENT`, `Tense.PAST`, `Tense.PERFECT`, `Tense.PAST_PERFECT`, `Tense.FUTURE`, `Tense.FUTURE_PERFECT` |
| Person | `Person.FIRST_SINGULAR`, `Person.SECOND_SINGULAR`, `Person.THIRD_SINGULAR`, `Person.FIRST_PLURAL`, `Person.SECOND_PLURAL`, `Person.THIRD_PLURAL` |
| Person (imperative) | `ImperativePerson.PERSON_2_SINGULAR`, `ImperativePerson.PERSON_2_PLURAL` |
| Infinitive forms | `InfinitiveForm.INFINITIVE_WITH_ZU`, `InfinitiveForm.PARTICIPLE_I`, `InfinitiveForm.PARTICIPLE_II` |

Note that not all mood and tense combinations are valid when conjugating a verb:
```python
> word.inflection.verb_conjugate(Mood.SUBJUNCTIVE_II, Tense.PRESENT, Person.FIRST_SINGULAR)
ValueError: Cannot inflect. Missing data for: 'Konjunktiv II'.'Präsens' . Did you mean 'Präteritum', 'Plusquamperfekt', 'Futur I', 'Futur II'?
```

Example:
```python
> inf = duden.get("laufen").inflection
> inf.verb_infinitive_forms(InfinitiveForm.PARTICIPLE_I)
'laufend'
```

## Word searching

### `get` function

The `duden.get` function requests directly the url `https://www.duden.de/rechtschreibung/{word}`, and retrieves a single parsed word. If the page was not found, returns `None`.

### `search` function

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

## Word of the day

Retrieves and parses the Word of the day from the main page.
```python
> duden.get_word_of_the_day
Quasimodogeniti (Substantiv ohne Artikel)
```
