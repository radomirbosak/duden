#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import unittest

import duden


JSON_DIR = 'test_data'


class TestDudenJsons(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.samples = []

        for filename in os.listdir(JSON_DIR):
            full_path = os.path.join(JSON_DIR, filename)
            if filename.endswith('.json'):
                with open(full_path, 'r') as fh:
                    word_json = json.load(fh)
                    word_obj = duden.DudenWord(word_json['urlname'])

                    cls.samples.append((word_json, word_obj))

    def _all_words_test(self, attribute_name):
        for word_json, word_obj in self.__class__.samples:
            with self.subTest(word=word_json['name']):
                real_value = getattr(word_obj, attribute_name)
                test_value = word_json[attribute_name]
                self.assertEqual(real_value, test_value)

    def test_title(self):
        self._all_words_test('title')

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

if __name__ == '__main__':
    unittest.main()
