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
                    word_obj = duden.DudenWord(word_json['name'])

                    cls.samples.append((word_json, word_obj))

    def test_title(self):
        for word_json, word_obj in self.__class__.samples:
            with self.subTest(word=word_json['name']):
                self.assertEqual(word_obj.title, word_json['title'])

if __name__ == '__main__':
    unittest.main()
