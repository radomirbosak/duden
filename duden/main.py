#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contains main duden functionality: DudenWord class, parsing, network requests.
"""

import copy
import gettext
import os

from crayons import blue, yellow, white  # pylint: disable=no-name-in-module

from .common import recursively_extract, table_node_to_tagged_cells
from .display import print_tree_of_strings


EXPORT_ATTRIBUTES = [
    'name', 'urlname', 'title', 'article', 'part_of_speech', 'usage',
    'frequency', 'word_separation', 'meaning_overview', 'origin', 'compounds',
    'grammar_raw', 'synonyms',
]

gettext.install('duden', os.path.join(os.path.dirname(__file__), 'locale'))


class DudenWord():
    """
    Represents parsed word. Takes a BeautifulSoup object as a constructor argument.

    Example:

        > r = requests.get('http://www.duden.de/rechtschreibung/Hase')
        > soup = bs4.BeautifulSoup(r.text)
        > word = duden.DudenWord(soup)
        > word
        Hase, der (Substantiv, maskulin)
    """
    wordcloud_parts_of_speech = ['substantive', 'verben', 'adjektive']

    def __init__(self, soup):
        self.soup = soup

    def __repr__(self):
        return '{} ({})'.format(self.title, self.part_of_speech)

    def describe(self):
        """
        Print overall word description
        """
        print(yellow(self.title, bold=True))
        print(yellow('=' * len(self.title)))

        if self.part_of_speech:
            print(white(_('Word type:'), bold=True), self.part_of_speech)
        if self.usage:
            print(white(_('Usage:'), bold=True), self.usage)
        if self.frequency:
            commonness = '{label} {frequency}{max_frequency}'.format(
                label=white(_('Commonness:'), bold=True),
                frequency=self.frequency,
                max_frequency=blue('/5'))
            print(commonness)
        if self.word_separation:
            print('{label} {content}'.format(
                label=white(_('Separation:'), bold=True),
                content=str(blue('|')).join(self.word_separation)))

        if self.meaning_overview:
            print(white(_('Meaning overview:'), bold=True))
            print_tree_of_strings(self.meaning_overview)

        if self.synonyms:
            print(white(_('Synonyms:'), bold=True))
            print_tree_of_strings(self.synonyms)

        if self.compounds:
            print(white(_('Typical compounds:'), bold=True))
            for part_of_speech, words in self.compounds.items():
                print(blue(' - {}:'.format(part_of_speech.capitalize())),
                      ', '.join(words))

    @property
    def title(self):
        """
        The word string with article
        """
        return self.soup.h1.get_text().replace('\xad', '').strip()

    @property
    def name(self):
        """
        Word without article
        """
        if ', ' not in self.title:
            return self.title

        name, _ = self.title.split(', ')
        return name

    @property
    def urlname(self):
        """
        Return unique representation of the word used in duden.de urls
        """
        return self.soup.head.link.attrs['href'].split('/')[-1]

    @property
    def article(self):
        """
        Word article
        """
        if ', ' not in self.title:
            return None

        _, article = self.title.split(', ')
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
        return None

    def _find_tuple_dl(self, key, element=None):
        """
        Get value element corresponding to key element containing the text
        provided by the `key` argument
        """
        if element is None:
            element = self.soup.article

        dls = element.find_all('dl', class_='tuple', recursive=False)
        for dl_node in dls:
            label = dl_node.find('dt', class_='tuple__key')
            if key in label.text:
                return dl_node.find('dd', class_='tuple__val')

        return None

    @property
    def part_of_speech(self):
        """
        Return the part of speech
        """
        try:
            pos_element = self._find_tuple_dl('Wortart')
            return pos_element.text
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
            freq_bar = self.soup.find('span', class_='shaft__full')
            return len(freq_bar.text)
        except AttributeError:
            return None

    @property
    def usage(self):
        """
        Return usage context
        """
        try:
            element = self._find_tuple_dl('Gebrauch')
            return element.text
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
                if approximate and name in section.h2.text:
                    return section
        return None

    @property
    def word_separation(self):
        """
        Return the word separated in a form of a list
        """
        containing_div = self.soup.find('div', id='rechtschreibung')
        sep_element = self._find_tuple_dl('Worttrennung', containing_div)
        if not sep_element:
            return None

        return sep_element.text.split('|')

    @property
    def meaning_overview(self):
        """
        Return the meaning structure, which can be string, list or a dict
        """
        section = self.soup.find('div', id='bedeutung') \
            or self.soup.find('div', id='bedeutungen')
        if section is None:
            return None
        section = copy.copy(section)
        section.header.extract()

        # 1. remove examples
        for dl_node in section.find_all('dl', class_='note'):
            if True or dl_node.dt.text == 'Beispiele':
                dl_node.extract()

        # 2. remove grammar parts
        for dl_node in section.find_all('dl', class_='tuple'):
            if dl_node.dt.text in ['Grammatik', 'Gebrauch']:
                dl_node.extract()

        # 3. remove pictures
        for node in section.find_all('figure'):
            node.extract()

        return recursively_extract(
            section, maxdepth=2, exfun=lambda x: x.text.strip())

    @property
    def synonyms(self):
        """
        Return the structure with word synonyms
        """
        try:
            section = self.soup.find('div', id='synonyme')
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
        section = self.soup.find('div', id='herkunft')
        if section is None:
            return None

        section = copy.copy(section)
        if section.header:
            section.header.extract()
        return section.text.strip()

    @property
    def compounds(self):
        """
        Return the typical word compounds
        """
        section = self.soup.find('div', id='kontext')
        if not section:
            return None

        pos_trans = {
            'noun': 'substantive',
            'verb': 'verben',
            'adj': 'adjektive',
        }

        compounds = {}

        cluster_element = section.find('figure', class_='tag-cluster__cluster')
        for a_node in cluster_element.find_all('a'):
            compound_word = a_node.text
            compound_type = pos_trans[a_node.attrs['data-group']]

            if compound_type not in compounds:
                compounds[compound_type] = []

            compounds[compound_type].append(compound_word)

        return compounds

    def grammar(self, *target_tags):
        """
        Return the information from grammar section

        Example:
        >>> word_laufen.grammar(duden.SINGULAR, duden.PRASENS, \
                                duden.INDIKATIV, duden.PERSON_3)
        ['er/sie/es läuft']
        """
        tagged_strings = self.grammar_raw
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
        section = self.soup.find('div', id='grammatik')
        if not section:
            return None

        table_nodes = self.soup.find_all('div', class_='wrap-table') \
            + self.soup.find_all('table', class_='mere-table')

        tagged_strings = []
        for table_node in table_nodes:
            tagged_strings.extend(table_node_to_tagged_cells(table_node))
        return tagged_strings

    def export(self):
        """
        Export word's attributes as a dictionary

        Used e.g. for creating test data.
        """
        worddict = dict()
        for attribute in EXPORT_ATTRIBUTES:
            worddict[attribute] = getattr(self, attribute, None)

        # convert grammar to lists
        listed_grammar = []
        for keylist, form in worddict['grammar_raw']:
            listed_grammar.append([list(keylist), form])
        worddict['grammar_raw'] = listed_grammar
        return worddict
