"""Test word functions"""

from duden.word import split_synonyms


def test_split_synonyms():
    """Test one-line list splitting"""
    assert split_synonyms("") == [""]
