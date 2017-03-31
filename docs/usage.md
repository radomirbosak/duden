# Usage

This example showcases the most useful functions of the `DudenWord` class.

```
> import duden
> w = duden.get('Barmherzigkeit')
> w.title
'Barmherzigkeit, die'

> w.name
'Barmherzigkeit'

> w.article
'die'

> w.part_of_speech
Substantiv, feminin

> w.frequency
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

> w.compounds
None

> w.grammar_raw
[({'Nominativ', 'Singular'}, 'die Barmherzigkeit'),
 ({'Genitiv', 'Singular'}, 'der Barmherzigkeit'),
 ({'Dativ', 'Singular'}, 'der Barmherzigkeit'),
 ({'Akkusativ', 'Singular'}, 'die Barmherzigkeit')]
```
