# -*- coding: utf-8 -*-
"""
The duden package can parse the https://www.duden.de/ word information.

The `get` function is used to return parsed word, when provided with the word's
exact url name. The `search` function is used to search for words, either
returning exact matches (homonyms), or if fuzzy search is enabled, similar
words.

The basic class representing the parsed word is `DudenWord`.
"""
__all__ = [
    "get",
    "search",
    "get_word_of_the_day",
    "SINGULAR",
    "PLURAL",
    "PRASENS",
    "PRATERITUM",
    "INDIKATIV",
    "IMPERATIV",
    "KONJUKTIV_1",
    "KONJUKTIV_2",
    "PARTIZIP_1",
    "PARTIZIP_2",
    "INFINITIV_MIT_ZU",
    "PERSON_1",
    "PERSON_2",
    "PERSON_3",
    "NOMINATIV",
    "GENITIV",
    "DATIV",
    "AKKUSATIV",
]

from .constants import (
    AKKUSATIV,
    DATIV,
    GENITIV,
    IMPERATIV,
    INDIKATIV,
    INFINITIV_MIT_ZU,
    KONJUKTIV_1,
    KONJUKTIV_2,
    NOMINATIV,
    PARTIZIP_1,
    PARTIZIP_2,
    PERSON_1,
    PERSON_2,
    PERSON_3,
    PLURAL,
    PRASENS,
    PRATERITUM,
    SINGULAR,
)
from .search import get, get_word_of_the_day, search
