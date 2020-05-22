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

import argparse
import copy
import gettext
import os
import sys
from itertools import cycle

import bs4
import requests
from crayons import blue, red, yellow, white

from .common import (recursively_extract, print_tree_of_strings,
                     clear_text, print_string_or_list)
from .__version__ import __version__


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

NOMINATIV = 'Nominativ'
GENITIV = 'Genitiv'
DATIV = 'Dativ'
AKKUSATIV = 'Akkusativ'

gettext.install('duden', os.path.join(os.path.dirname(__file__), 'locale'))


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
        The word string
        """
        return self.soup.h1.get_text().replace('\xad', '').strip()

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

    def _find_tuple_dl(self, key, element=None):
        """
        Get value element corresponding to key element containing the text
        provided by the `key` argument
        """
        if element is None:
            element = self.soup.article

        dls = element.find_all('dl', class_='tuple', recursive=False)
        for dl in dls:
            label = dl.find('dt', class_='tuple__key')
            if key in label.text:
                return dl.find('dd', class_='tuple__val')

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
                elif approximate and name in section.h2.text:
                    return section
        else:
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
        for dl in section.find_all('dl', class_='note'):
            if True or dl.dt.text == 'Beispiele':
                dl.extract()

        # 2. remove grammar parts
        for dl in section.find_all('dl', class_='tuple'):
            if dl.dt.text in ['Grammatik', 'Gebrauch']:
                dl.extract()

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
        for a in cluster_element.find_all('a'):
            compound_word = a.text
            compound_type = pos_trans[a.attrs['data-group']]

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

        title_element = table_node.h3
        table_name = title_element.text if title_element else ''

        # convert table html node to raw table (list of lists) and optional
        # left and top headers (also lists)
        if table_node.thead:
            all_ths = table_node.thead.find_all(
                'th', class_='wrap-table__flexions-head')
            top_header = [clear_text(t.text) for t in all_ths]

        for row in table_node.tbody.find_all('tr'):
            if row.th:
                th = row.th
                rowspan = int(th.attrs.get('rowspan', 1))
                left_header.extend([clear_text(row.th.text)] * rowspan)

            tds = row.find_all('td')
            table_content.append([clear_text(td.text) for td in tds])

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
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        raise Exception(_("Connection could not be established. "
                          "Check your internet connection."))

    code = response.status_code
    if code == 200:
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
    elif code == 404:
        # non-existent word
        return None
    else:
        raise Exception(
            _("Unexpected HTTP response status code {}").format(code))

    return load_soup(soup)


def load_soup(soup):
    """
    Load the DudenWord instance using a BeautifulSoup object
    """
    return DudenWord(soup)


def get_search_link_variants(link_text):
    """
    Lists possible interpretations of link text on search page.

    Used for determining whether a search page entry matches the search term.
    """
    return clear_text(link_text).split(', ')


def search(word, exact=True, return_words=True):
    """
    Search for a word 'word' in duden
    """
    url = SEARCH_URL_FORM.format(word=word)
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    definitions = soup.find_all('h2', class_='vignette__title')

    if definitions is None:
        return []

    urlnames = []
    for definition in definitions:
        definition_title = definition.text
        if (not exact) or word in get_search_link_variants(definition_title):
            urlnames.append(definition.find('a')['href'].split('/')[-1])

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
    parser.add_argument('--title', action='store_true',
                        help=_('display word and article'))
    parser.add_argument('--name', action='store_true',
                        help=_('display the word itself'))
    parser.add_argument('--article', action='store_true',
                        help=_('display article'))
    parser.add_argument('--part-of-speech', action='store_true',
                        help=_('display part of speech'))
    parser.add_argument('--frequency', action='store_true',
                        help=_('display commonness (1 to 5)'))
    parser.add_argument('--usage', action='store_true',
                        help=_('display context of use'))
    parser.add_argument('--word-separation', action='store_true',
                        help=_('display proper separation (line separated)'))
    parser.add_argument('--meaning-overview', action='store_true',
                        help=_('display meaning overview'))
    parser.add_argument('--synonyms', action='store_true',
                        help=_('list synonyms (line separated)'))
    parser.add_argument('--origin', action='store_true',
                        help=_('display origin'))
    parser.add_argument('--compounds', nargs='?', const='ALL',
                        help=_('list common compounds'))
    parser.add_argument('-g', '--grammar', nargs='?', const='ALL',
                        help=_('list grammar forms'))

    parser.add_argument('-r', '--result', type=int,
                        help=_('display n-th (starting from 1) result in case '
                               'of multiple words matching the input'))
    parser.add_argument('--fuzzy', action='store_true',
                        help=_('enable fuzzy word matching'))

    parser.add_argument('-V', '--version', action='store_true',
                        help=_('print program version'))

    return parser.parse_args()


def display_word(word, args):
    if args.title:
        print(word.title)
    elif args.name:
        print(word.name)
    elif args.article:
        if word.article:
            print(word.article)
    elif args.part_of_speech:
        if word.part_of_speech:
            print(word.part_of_speech)
    elif args.frequency:
        if word.frequency:
            print(word.frequency)
    elif args.usage:
        if word.usage:
            print(word.usage)
    elif args.word_separation:
        for part in word.word_separation:
            print(part)
    elif args.meaning_overview:
        if word.meaning_overview:
            print_tree_of_strings(word.meaning_overview)
    elif args.synonyms:
        synonyms = word.synonyms
        if synonyms:
            print_string_or_list(synonyms)
    elif args.origin:
        if word.origin:
            print(word.origin)
    elif args.compounds:
        if word.compounds:
            if args.compounds == 'ALL':
                for part_of_speech, compounds in word.compounds.items():
                    print(white('# ' + part_of_speech.capitalize(), bold=True))
                    print_string_or_list(compounds)
                    print()
            else:
                print_string_or_list(word.compounds[args.compounds])
    elif args.grammar:
        display_grammar(word, args.grammar)
    else:
        # print the description
        word.describe()


def display_grammar(word, grammar_args):
    grammar_struct = word.grammar_raw
    if grammar_struct is None:
        return

    grammar_tokens = [token.lower() for token in grammar_args.split(',')]

    table = []
    for keys, value in word.grammar_raw:
        lkeys = {key.lower() for key in keys}

        if not (grammar_args == 'ALL' or lkeys.issuperset(grammar_tokens)):
            continue

        reduced_keys = lkeys.difference(grammar_tokens)
        keystring = ' '.join(reduced_keys)

        if keystring:
            row = list(reduced_keys) + [blue("|"), value]
        else:
            row = [value]
        table.append(row)
    display_table(table)


def display_table(table, cell_spacing=' '):
    cols = list(zip(*table))
    collens = [max(len(word) for word in col) for col in cols]

    for row in table:
        for elem, collen in zip(row, collens):
            print(elem.ljust(collen), end=cell_spacing)
        print()


def main():
    """
    Take the first CLI argument and describe the corresponding word
    """

    # handle the --version switch
    if '--version' in sys.argv:
        print('duden ' + __version__)
        sys.exit(0)

    # parse normal arguments
    args = parse_args()

    # search all words matching the string
    words = search(args.word, return_words=False, exact=not args.fuzzy)

    # exit if the word wasn't found
    if not words:
        print(red(_("Word '{}' not found")).format(args.word))
        sys.exit(1)

    # list the options when there is more than one matching word
    if len(words) > 1 and args.result is None:
        print(_('Found {} matching words. Use the -r/--result argument to '
                'specify which one to display.').format(white(len(words),
                                                              bold=True)))
        for i, word in enumerate(words, 1):
            print('{} {}'.format(blue('{})'.format(i)), word))
        sys.exit(1)

    result_index = args.result if args.result is not None else 1

    # choose the correct result
    try:
        word_url_suffix = words[result_index - 1]
    except IndexError:
        print(red(_("No result with number {}.")).format(result_index))
        sys.exit(1)

    # fetch and parse the word
    try:
        word = get(word_url_suffix)
    except Exception as exception:
        print(red(exception))
        sys.exit(1)

    display_word(word, args)


if __name__ == '__main__':
    main()
