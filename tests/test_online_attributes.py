import os
import json
from collections import namedtuple

import pytest

import duden.main as duden


JSON_DIR = 'tests/test_data'

WordTestRecord = namedtuple('WordTestRecord', ["parsed_word", "expected_json"])


def generate_word_data():
    data = []
    for filename in os.listdir(JSON_DIR):
        full_path = os.path.join(JSON_DIR, filename)

        # read only json files
        if not filename.endswith('.json'):
            continue

        # store real and expected result
        with open(full_path, 'r') as fh:
            expected_json = json.load(fh)
        parsed_word = duden.get(expected_json['urlname'])

        record = WordTestRecord(parsed_word, expected_json)
        data.append(record)
    return data


# set up test parameters matrix
word_data = generate_word_data()

basic_attributes = [
    'title', 'name', 'article', 'part_of_speech', 'frequency', 'usage',
    'word_separation', 'meaning_overview', 'synonyms', 'origin', 'compounds'
]

word_param = pytest.mark.parametrize("parsed_word,expected_json", word_data)
attribute_param = pytest.mark.parametrize("attribute", basic_attributes)


@word_param
@attribute_param
def test_basic_attributes(parsed_word, expected_json, attribute):
    assert getattr(parsed_word, attribute) == expected_json[attribute]


@word_param
def test_word_grammar(parsed_word, expected_json):
    expected_grammar = expected_json['grammar_raw']
    if expected_grammar is not None:
        expected_grammar = [(set(tags), string)
                            for tags, string in expected_grammar]

    assert parsed_word.grammar_raw == expected_grammar
