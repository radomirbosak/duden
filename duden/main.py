#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dudendown

This script takes a german word as a commandline input and returns its meaning
overview, as parsed from the dictionary on the website `www.duden.de`.

Words with non-ascii characters should be given using following
transliteration:
* ä -> ae
* ö -> oe
* ü -> ue
* ß -> sz
"""

import sys
import copy
import argparse
from itertools import cycle

import bs4
import requests

from duden.common import recursively_extract, print_tree_of_strings, clear_text


URL_FORM = 'http://www.duden.de/rechtschreibung/{word}'
SEARCH_URL_FORM = 'http://www.duden.de/suchen/dudenonline/{word}'

# grammar forms constants
SINGULAR = 'Singular'
PLURAL = 'Plural'

PRASENS = 'Präsens'
PRATERITUM = 'Präteritum'

INDIKATIV = 'Indikativ'
IMPERATIV = 'Imperativ'
KONJUKTIV_1 = 'Konjunktiv I'
KONJUKTIV_2 = 'Konjunktiv II'

PARTIZIP_1 = 'Partizip I'
PARTIZIP_2 = 'Partizip II'
INFINITIV_MIT_ZU = 'Infinitiv mit zu'

PERSON_1 = 'Person I'
PERSON_2 = 'Person II'
PERSON_3 = 'Person III'


class DudenWord():

    wordcloud_parts_of_speech = ['substantive', 'verben', 'adjektive']

    def __init__(self, soup):
        self.soup = soup

    def __repr__(self):
        return '{} ({})'.format(self.title, self.part_of_speech)

    def describe(self):
        """
        Print overall word description
        """
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

        if self.synonyms:
            print('Synonyms:')
            print_tree_of_strings(self.synonyms)

        if self.compounds:
            print('Typical compounds:')
            for part_of_speech, words in self.compounds.items():
                print(' - {}: {}'.format(part_of_speech, ', '.join(words)))

    @property
    def title(self):
        """
        The word string
        """
        return self.soup.h1.get_text().replace('\xad', '')

    @property
    def name(self):
        """
        Word together with its article
        """
        if ', ' not in self.title:
            return self.title
        else:
            name, article = self.title.split(', ')
            return name

    @property
    def article(self):
        """
        Word article
        """
        if ', ' not in self.title:
            return None
        else:
            name, article = self.title.split(', ')
            return article

    def _section_main_get_node(self, name, use_label=True):
        """
        Return the div in main section which contains the text `name` as label
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
        """
        Return the part of speech
        """
        try:
            pos_div = self._section_main_get_node('Wortart:')
            return pos_div.strong.text
        except AttributeError:
            return None

    @property
    def frequency(self):
        """
        Return word frequency:

        0 - least frequent
        5 - most frequent
        """
        try:
            pos_div = self._section_main_get_node(
                'Häufigkeit:', use_label=False)
            return pos_div.strong.text.count('▮')
        except AttributeError:
            return None

    @property
    def usage(self):
        """
        Return usage context
        """
        try:
            pos_div = self._section_main_get_node('Gebrauch:')
            return pos_div.strong.text
        except AttributeError:
            return None

    def _find_section(self, name, approximate=False):
        """
        Return the section which has <h2> tag with title `name`

        If approximate is True, it is sufficient that `name` is a substring of
        the <h2> title's string.

        If no matching section is found, None is returned.
        """
        for section in self.soup.find_all('section'):
            if section.h2:
                if name == section.h2.text:
                    return section
                elif approximate and name in section.h2.text:
                    return section
        else:
            return None

    @property
    def word_separation(self):
        """
        Return the word separated in a form of a list
        """
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
        """
        Return the meaning structure, which can be string, list or a dict
        """
        try:
            section = self._find_section('Bedeutungsübersicht')
        except AttributeError:
            return None

        if section is None:
            return None

        node = copy.copy(section)

        # remove the meaning overview header
        if node.header:
            node.header.extract()

        # remove examples
        if node.section and node.section.h3.text == 'Beispiele':
            node.section.extract()

        # remove figures
        while node.figure:
            node.figure.extract()

        return recursively_extract(node, maxdepth=2,
                                   exfun=lambda x: x.text.strip())

    @property
    def synonyms(self):
        """
        Return the structure with word synonyms
        """
        try:
            section = self._find_section('Synonyme zu', approximate=True)
            section = copy.copy(section)
            if section.header:
                section.header.extract()
            return recursively_extract(section, maxdepth=2,
                                       exfun=lambda x: x.text.strip())
        except AttributeError:
            return None

    @property
    def origin(self):
        """
        Return the word origin
        """
        section = self._find_section('Herkunft')
        if section is None:
            return None

        section = copy.copy(section)
        if section.header:
            section.header.extract()
        return section.text

    @property
    def compounds(self):
        """
        Return the typical word compounds
        """
        section = self._find_section('Typische Verbindungen', approximate=True)
        if not section:
            return None

        d = {}
        for pos in DudenWord.wordcloud_parts_of_speech:
            word_cloud = section.find(id=pos)
            if word_cloud:
                words = [a.text for a in word_cloud.find_all('a')] \
                    if word_cloud else []
                d[pos] = words
        return d

    def grammar(self, *target_tags):
        """
        Return the information from grammar section

        Example:
        >>> word_laufen.grammar(duden.SINGULAR, duden.PRASENS, \
                                duden.INDIKATIV, duden.PERSON_3)
        ['er/sie/es läuft']
        """
        tagged_strings = self.grammar_raw()
        target_tags = set(target_tags)
        return [string
                for tags, string in tagged_strings
                if target_tags.issubset(tags)]

    @property
    def grammar_raw(self):
        """
        Find the Grammar sections in the document and extract tagged string
        list of all tables found there.

        The concatinated tagged string list (for all tables) is returned
        """
        section = self._find_section('Grammatik')
        if not section:
            return None

        table_nodes = section.find_all('table')

        tagged_strings = []
        for table_node in table_nodes:
            tagged_strings.extend(
                self._table_node_to_tagged_cells(table_node))
        return tagged_strings

    def _table_node_to_tagged_cells(self, table_node):
        """
        Takes a table HTML node and returns the list of table cell strings
        tagged using the table top and left header (optionally using the table
        name found in the upper-leftmost cell).

        The return type is a list of 2-tuples:
        [(tag_set, text), ...]

        where text is a string taken from the cell, and tag_set is a set of
        strings (tags). If e.g. cell in the 3rd row and 2nd column with the
        text 'der Barmherzigkeit', has its top_header tag (1st row, 2nd
        column) 'Singular' and its left_header tag (1st column, 3rd row)
        'Genitiv', the corresponding tuple would look like:
        ({'Singular', 'Genitiv'}, 'der Barmherzigkeit')
        .

        The first row is considered a header row, if it's inside of <thead>
        html tag. The first column is considered a header column if the
        corresponding cells are <th> html nodes.
        """
        left_header = []
        top_header = None
        table_content = []
        table_name = ''

        # convert table html node to raw table (list of lists) and optional
        # left and top headers (also lists)
        if table_node.thead:
            top_header = [clear_text(t.text)
                          for t in table_node.thead.find_all('th')]

        for row in table_node.tbody.find_all('tr'):
            if row.th:
                left_header.append(clear_text(row.th.text))

            tds = row.find_all('td')
            table_content.append([clear_text(td.text) for td in tds])

        if top_header and left_header:
            table_name = top_header[0]
            top_header = top_header[1:]

        # sanitize missing cells
        last_nonempty_cell = ''
        for i, cell in enumerate(left_header):
            if cell == '':
                left_header[i] = last_nonempty_cell
            else:
                last_nonempty_cell = cell

        # convert left, top, and table headers to sets for easier tagging
        if left_header:
            left_header = [{cell} for cell in left_header]
        else:
            left_header = [set() for _ in table_content]
        if top_header:
            top_header = [{cell} for cell in top_header]
        else:
            top_header = [set() for _ in table_content[0]]
        table_tag = {table_name} if table_name else set()

        if table_name in [PRASENS, PRATERITUM]:
            person_tags = [{PERSON_1}, {PERSON_2}, {PERSON_3}]
        else:
            person_tags = [set(), set(), set()]

        # create a list of tagged strings
        tagged_strings = []
        for row, row_tag, person_tag \
                in zip(table_content, left_header, cycle(person_tags)):
            for cell, col_tag in zip(row, top_header):
                taglist = table_tag \
                    .union(row_tag) \
                    .union(col_tag) \
                    .union(person_tag)
                tagged_strings.append((taglist, cell))
        return tagged_strings


def get(word):
    """
    Load the word 'word' and return the DudenWord instance
    """
    url = URL_FORM.format(word=word)
    response = requests.get(url)

    code = response.status_code
    if code == 200:
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
    elif code == 404:
        # non-existent word
        return None
    else:
        raise Exception(
            "Unexpected HTTP response status code {}".format(code))

    return load_soup(soup)


def load_soup(soup):
    """
    Load the DudenWord instance using a BeautifulSoup object
    """
    return DudenWord(soup)


def search(word, exact=True, return_words=True):
    """
    Search for a word 'word' in duden
    """
    url = SEARCH_URL_FORM.format(word=word)
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    main_sec = soup.find('section', id='block-duden-tiles-0')
    a_tags = [h2.a for h2 in main_sec.find_all('h2')]

    urlnames = [a['href'].split('/')[-1]
                for a in a_tags
                if (not exact) or clear_text(a.text) == word]
    if return_words:
        return [get(urlname) for urlname in urlnames]
    else:
        return urlnames


def parse_args():
    """
    Parse CLI arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('word')
    return parser.parse_args()


def main():
    """
    Take the first CLI argument and describe the corresponding word
    """
    args = parse_args()

    # load and parse the word
    word = get(args.word)

    # exit if the word wasn't found
    if word is None:
        print("Word '{}' not found".format(args.word))
        sys.exit(1)

    # print the description
    word.describe()


if __name__ == '__main__':
    main()
