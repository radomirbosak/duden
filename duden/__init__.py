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
]

# grammatical categories enums
from .inflection import (
    Case,
    Degree,
    Gender,
    ImperativePerson,
    InfinitiveForm,
    Mood,
    Number,
    Person,
    Tense,
)
from .request import get, get_word_of_the_day, search
