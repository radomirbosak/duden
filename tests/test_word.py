"""Test word functions"""

from duden.word import split_synonyms


def test_split_synonyms():
    """Test one-line list splitting"""
    assert split_synonyms("") == [""]
    assert split_synonyms("a, b ,c") == ["a", "b", "c"]

    expected = ["a", "b (b, c)", "d (d, e, f) g", "h"]
    assert split_synonyms("a, b (b, c); d (d; e, f) g, h") == expected
