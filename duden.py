#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import bs4
import sys
import copy
import requests

from common import recursively_extract, print_tree_of_strings


URL_FORM = 'http://www.duden.de/rechtschreibung/{word}'


class DudenWord():

    def __init__(self, word):
        self.query = word
        url = URL_FORM.format(word=word)
        response = requests.get(url)

        code = response.status_code
        if code == 200:
            self._exists = True
            self.soup = bs4.BeautifulSoup(response.text, 'html.parser')
        elif code == 404:
            self._exists = False
        else:
            raise Exception(
                "Unexpected HTTP response status code {}".format(code))

    @property
    def exists(self):
        return self._exists

    def describe(self):
        if not self.exists:
            print('\'{}\' not found'.format(self.query))
            return

        print(self.title)
        print('=' * len(self.title))

        print('Word type: ' + self.part_of_speech)
        if self.usage:
            print('Usage: ' + self.usage)
        print('Commonness: {}/5'.format(self.frequency))
        if self.word_separation:
            print('Separation: ' + '|'.join(self.word_separation))

        if self.meaning_overview:
            print('Meaning overview:')
            print_tree_of_strings(self.meaning_overview)

    @property
    def title(self):
        return self.soup.h1.get_text().replace('\xad', '')

    def _section_main_get_node(self, name, use_label=True):
        """
        Return the div in main section which contains the text <name> as label
        """
        section = self.soup.find('section', id='block-system-main')
        entry = section.find('div', class_='entry')
        for div in entry.find_all('div'):
            labelnode = div.find('span', class_='label') if use_label else div

            if name in labelnode.text:
                return div
        else:
            return None

    def _section_other_get_div(self, name, section, use_label=True):
        entries = section.find_all('div', class_='entry')
        for div in entries:
            labelnode = div.find('span', class_='label') if use_label else div

            if name in labelnode.text:
                return div
        else:
            return None

    @property
    def part_of_speech(self):
        try:
            pos_div = self._section_main_get_node('Wortart:')
            return pos_div.strong.text
        except AttributeError:
            return None

    @property
    def frequency(self):
        try:
            pos_div = self._section_main_get_node(
                'Häufigkeit:', use_label=False)
            return pos_div.strong.text.count('▮')
        except AttributeError:
            return None

    @property
    def usage(self):
        try:
            pos_div = self._section_main_get_node('Gebrauch:')
            return pos_div.strong.text
        except AttributeError:
            return None

    def _find_section(self, name):
        for section in self.soup.find_all('section'):
            if section.h2 and name == section.h2.text:
                return section
        else:
            return None

    @property
    def word_separation(self):
        try:
            section = self._find_section('Rechtschreibung')
            div = self._section_other_get_div('Worttrennung:', section,
                                              use_label=False)
            return div.find('span', class_='lexem').text.split('|')
        except AttributeError:
            pass

        # If the word_separation was not found in the Rechtschreibung section
        # we try it again in the main section (see e.g. word 'Qat').
        try:
            div = self._section_main_get_node('Worttrennung:')
            div = copy.copy(div)
            label = div.find('span', class_='label')
            label.extract()
            return div.text.strip().split('|')
        except AttributeError:
            return None

    @property
    def meaning_overview(self):
        try:
            section = self._find_section('Bedeutungsübersicht')
            entry = section.find(class_='entry')
        except AttributeError:
            return None
        entry = copy.copy(entry)

        # remove examples
        if entry.section and entry.section.h3.text == 'Beispiele':
            entry.section.extract()

        return recursively_extract(entry, maxdepth=2,
                                   exfun=lambda x: x.text.strip())


def get(word):
    return DudenWord(word)


def main():
    if len(sys.argv) < 2:
        print('Usage:')
        print('python3 duden.py <WORD>')
        sys.exit(1)

    word = get(sys.argv[1])
    word.describe()


if __name__ == '__main__':
    main()
