# -*- coding: utf-8 -*-
"""
Test if words currently available online parse as expected
"""
import os
from collections import namedtuple

import pytest
import yaml

from duden import get

TEST_DATA_DIR = "tests/test_data"

WordTestRecord = namedtuple("WordTestRecord", ["parsed_word", "expected_dict"])


def iterate_test_yaml():
    """
    Iterate over .yaml file contents in test data directory
    """
    for filename in os.listdir(TEST_DATA_DIR):
        full_path = os.path.join(TEST_DATA_DIR, filename)

        # read only yaml files
        if not filename.endswith(".yaml"):
            continue

        # store real and expected result
        with open(full_path, "r", encoding="UTF-8") as file:
            yield yaml.load(file, Loader=yaml.SafeLoader)


def generate_word_data():
    """
    Download actual words from duden corresponding to test words from `TEST_DATA_DIR`
    """
    return [
        WordTestRecord(get(expected_dict["urlname"]), expected_dict)
        for expected_dict in iterate_test_yaml()
    ]


# set up test parameters matrix
word_data = generate_word_data()

basic_attributes = [
    "title",
    "name",
    "article",
    "part_of_speech",
    "frequency",
    "usage",
    "word_separation",
    "synonyms",
    "origin",
    "grammar_overview",
    "words_before",
    "words_after",
    "phonetic",
]

word_param = pytest.mark.parametrize("parsed_word,expected_dict", word_data)
attribute_param = pytest.mark.parametrize("attribute", basic_attributes)


@word_param
@attribute_param
def test_basic_attributes(parsed_word, expected_dict, attribute):
    """Test basic word attributes"""
    assert getattr(parsed_word, attribute) == expected_dict[attribute]


@word_param
def test_meaning_overview(parsed_word, expected_dict):
    """Test meaning overview attribute"""
    assert parsed_word.meaning_overview == expected_dict["meaning_overview"]


@word_param
def test_word_compounds(parsed_word, expected_dict):
    """Test word compounds attribute"""
    parsed = parsed_word.compounds
    expected = expected_dict["compounds"]

    if parsed == expected == None:  # noqa
        return

    assert parsed.keys() == expected.keys()

    if "substantive" in expected:
        assert set(parsed["substantive"]) == set(expected["substantive"])

    if "verben" in expected:
        assert set(parsed["verben"]) == set(expected["verben"])

    if "adjektive" in expected:
        assert set(parsed["adjektive"]) == set(expected["adjektive"])


@word_param
def test_word_inflection(parsed_word, expected_dict):
    """The the raw inflection tables data"""
    raw_parsed_inf_data = parsed_word.inflection and parsed_word.inflection.data
    assert raw_parsed_inf_data == expected_dict["inflection"]
