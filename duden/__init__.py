# -*- coding: utf-8 -*-
"""
The duden package can parse the http://www.duden.de/ word information.

The `get` function is used to return parsed word, when provided with the word's
exact url name. The `search` function is used to search for words, either
returning exact matches (homonyms), or if fuzzy search is enabled, similar
words.

The basic class representing the parsed word is `DudenWord`.
"""
__all__ = [
    'get', 'search',
    'SINGULAR', 'PLURAL',
    'PRASENS', 'PRATERITUM',
    'INDIKATIV', 'IMPERATIV', 'KONJUKTIV_1', 'KONJUKTIV_2',
    'PARTIZIP_1', 'PARTIZIP_2', 'INFINITIV_MIT_ZU',
    'PERSON_1', 'PERSON_2', 'PERSON_3',
    'NOMINATIV', 'GENITIV', 'DATIV', 'AKKUSATIV'
]

from .search import get, search

from .constants import (SINGULAR, PLURAL,
                        PRASENS, PRATERITUM,
                        INDIKATIV, IMPERATIV, KONJUKTIV_1, KONJUKTIV_2,
                        PARTIZIP_1, PARTIZIP_2, INFINITIV_MIT_ZU,
                        PERSON_1, PERSON_2, PERSON_3,
                        NOMINATIV, GENITIV, DATIV, AKKUSATIV)
