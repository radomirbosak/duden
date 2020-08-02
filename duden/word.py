#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contains the DudenWord class: a parser of duden.de response.
"""

import copy
import gettext
import os

from .common import recursively_extract, table_node_to_tagged_cells, clear_text


EXPORT_ATTRIBUTES = [
    'name', 'urlname', 'title', 'article', 'part_of_speech', 'usage',
    'frequency', 'word_separation', 'meaning_overview', 'origin', 'compounds',
    'grammar_raw', 'synonyms', 'words_before', 'words_after'
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
    # pylint: disable=too-many-public-methods
    wordcloud_parts_of_speech = ['substantive', 'verben', 'adjektive']

    def __init__(self, soup):
        self.soup = soup

    def __repr__(self):
        return '{} ({})'.format(self.title, self.part_of_speech)

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
    def revision_url(self):
        """Returns url to this specific word revision"""
        return self.soup.find('input', id='cite-field').attrs['value']

    @property
    def node_no(self):
        """Returns word node number"""
        return self.revision_url.split('/')[-3]

    @property
    def revision_no(self):
        """Returns word revision number"""
        return self.revision_url.split('/')[-1]

    @property
    def article(self):
        """
        Word article
        """
        if ', ' not in self.title:
            return None

        _, article = self.title.split(', ')
        return article

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

        compounds_sorted = {}
        for pos in sorted(compounds.keys()):
            compounds_sorted[pos] = sorted(compounds[pos])

        return compounds_sorted

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
        if worddict['grammar_raw'] is not None:
            listed_grammar = []
            for keylist, form in worddict['grammar_raw']:
                listed_grammar.append([sorted(keylist), form])
            worddict['grammar_raw'] = listed_grammar
        return worddict

    @property
    def before_after_structure(self):
        """
        Parsed "Blätter section"

        Returns: dict mapping section names to list of words tuples.
                 Each tuple is comprised of word name and word urlname.

        Example:
            >>> duden.get("laufen").before_after_structure
            {'Im Alphabet davor': [('Laufbekleidung', 'Laufbekleidung'),
              ('Laufbrett', 'Laufbrett'),
              ('Laufbursche', 'Laufbursche'),
              ('Läufchen', 'Laeufchen'),
              ('Läufel', 'Laeufel')],
             'Im Alphabet danach': [('laufend', 'laufend'),
              ('laufen lassen, laufenlassen', 'laufen_lassen'),
              ('Laufer', 'Laufer'),
              ('Läufer', 'Laeufer'),
              ('Lauferei', 'Lauferei')]}
        """
        result = {}
        section = self.soup.find('div', id='block-beforeafterblock-2')
        for group in section.find_all('nav', class_='hookup__group'):
            h3title = group.h3.text
            result[h3title] = []
            for item in group.find_all('li'):
                link = item.a.attrs['href'].split('/')[-1]
                result[h3title].append((clear_text(item.text), link))
        return result

    @property
    def words_before(self):
        """Returns 5 words before this one in duden database"""
        return [name for name, _ in self.before_after_structure['Im Alphabet davor']]

    @property
    def words_after(self):
        """Returns 5 words after this one in duden database"""
        return [name for name, _ in self.before_after_structure['Im Alphabet danach']]
