#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import unittest

import bs4
import requests

import duden


JSON_DIR = 'tests/test_data'


class TestDudenJsons(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.samples = []

        for filename in os.listdir(JSON_DIR):
            full_path = os.path.join(JSON_DIR, filename)
            if filename.endswith('.json'):
                with open(full_path, 'r') as fh:
                    word_json = json.load(fh)
                    word_obj = duden.get(word_json['urlname'])

                    cls.samples.append((word_json, word_obj))

    def _all_words_test(self, attribute_name, transorm_test_data=None):
        for word_json, word_obj in self.__class__.samples:
            with self.subTest(word=word_json['name']):
                real_value = getattr(word_obj, attribute_name)
                test_value = word_json[attribute_name]
                if transorm_test_data:
                    test_value = transorm_test_data(test_value)
                self.assertEqual(real_value, test_value)

    def test_title(self):
        self._all_words_test('title')

    def test_name(self):
        self._all_words_test('name')

    def test_article(self):
        self._all_words_test('article')

    def test_part_of_speech(self):
        self._all_words_test('part_of_speech')

    def test_frequency(self):
        self._all_words_test('frequency')

    def test_usage(self):
        self._all_words_test('usage')

    def test_word_separation(self):
        self._all_words_test('word_separation')

    def test_meaning_overview(self):
        self._all_words_test('meaning_overview')

    def test_synonyms(self):
        self._all_words_test('synonyms')

    def test_origin(self):
        self._all_words_test('origin')

    def test_compounds(self):
        self._all_words_test('compounds')

    def test_grammar_raw(self):
        def grammar_data_change(raw_grammar_data):
            if raw_grammar_data is None:
                return None
            return [(set(tags), string) for tags, string in raw_grammar_data]

        self._all_words_test('grammar_raw',
                             transorm_test_data=grammar_data_change)


class TestDuden(unittest.TestCase):

    def test_get(self):
        word = 'laufen'
        dword = duden.get('laufen')
        self.assertEqual(word, dword.title)

    def test_load_soup(self):
        word = 'laufen'
        url = duden.URL_FORM.format(word=word)
        r = requests.get(url)
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        dword = duden.load_soup(soup)
        self.assertEqual(word, dword.title)


if __name__ == '__main__':
    unittest.main()
