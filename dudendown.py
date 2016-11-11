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

from enum import Enum
from string import ascii_lowercase

import requests

from bs4 import BeautifulSoup


class Sections(Enum):
    """
    Common sections found on a page of any word
    """
    grammar = "Grammatik"
    pronounciation = "Aussprache"
    correct_writing = "Rechtschreibung"
    meaning_overview = "Bedeutungsübersicht"
    synonyms = "Synonyme"
    meanings = "Bedeutungen,"
    letters = "Blättern"


def recursively_extract(node, exfun, maxdepth=2):
    """
    Transform a html ul/ol tree into a python list tree.

    Converts a html node containing ordered and unordered lists and list items
    into an object of lists with tree-like structure. Leaves are retrieved by
    applying `exfun` function to the html nodes not containing any ul/ol list.

    Args:
        node: BeautifulSoup HTML node to traverse
        exfun: function to apply to every string node found
        maxdepth: maximal depth of lists to go in the node

    Returns:
        A tree-like python object composed of lists.


    Examples:

    >>> node_content = \
    '''
    <ol>
        <li>Hase</li>
        <li>Nase<ol><li>Eins</li><li>Zwei</li></ol></li>
    </ol>'''
    >>> node = BeautifulSoup(node_content, "lxml")
    >>> recursively_extract(node, lambda x: x)
    [<li>Hase</li>, [<li>Eins</li>, <li>Zwei</li>]]
    >>> recursively_extract(node, lambda x: x.get_text())
    ['Hase', ['Eins', 'Zwei']]
    """
    lilist = node.ol or node.ul
    if lilist and maxdepth:
        # apply 'recursively_extract' to every 'li' node found under this node
        return [recursively_extract(li, exfun, maxdepth=(maxdepth - 1))
                for li in lilist.find_all('li', recursive=False)]
    # if this node doesn't contain 'ol' or 'ul' node, return the transformed
    # leaf (using the 'exfun' function)
    return exfun(node)


def meaning_fun(node):
    """
    Extract stripped text from node

    Args:
        node: HTML node to extract from

    Return:
        extracted string
    """
    return node.get_text().strip()


def print_meaning(meaning):
    """
    Print a tree of strings up to depth 2

    Args:
        meaning: tree of strings

    Example:

    >>> print_meaning(['Hase', ['Eins', 'Zwei']])
    0. Hase
    <BLANKLINE>
    1.  a. Eins
        b. Zwei
    """
    for i1, m1 in enumerate(meaning):
        if type(m1) is str:
            print("{:>2}. {}".format(i1, m1))
        elif type(m1) is list:
            for i2, m2 in zip(ascii_lowercase, m1):
                indent = "{:>2}. ".format(i1) if i2 == 'a' else " " * 4
                print("{} {}. {}".format(indent, i2, m2))
        print()


def correct_parenthesis(text):
    """
    Convert semincolons inside parentheses to commas.
    Convert commas outside parentheses to semincolons.

    Args:
        text: string to transform

    Returns:
        Corrected text

    Example:

    >>> correct_parenthesis('a, b; c (d, e; f)')
    'a; b; c (d, e, f)'
    """
    newtext = []
    inner = False
    for l in text:
        # if '(' was found, switch to True
        # if ')' was found, switch to False
        inner = (l == "(") if (l in "()") else inner
        if inner and l == ";":
            l = ","
        elif not inner and l == ',':
            l = ";"
        newtext.append(l)
    return ''.join(newtext)


def extract_synonym_from_li(node):
    """
    Convert a node containing synonym overview to a list of strings

    Args:
        li: a html node to convert

    Returns:
        list of strings

    Example:

    >>> li_content = 'a, b; c (d, e; f)'
    >>> li_node = BeautifulSoup('<li>' + li_content + '</li>', 'lxml').li
    >>> extract_synonym_from_li(li_node)
    ['a', 'b', 'c (d, e, f)']
    """
    totaltext = correct_parenthesis(node.get_text())
    return [synonym.strip() for synonym in totaltext.split(';')]


def meaning_struct_from_li(li):
    """
    Convert a 'li' html node to dict containing text and section information

    All text descriptions of images are removed.

    Args:
        li: a html node to convert

    Returns:
        A dictionary containing text and section information extracted from
        the provided html node

    Example:

    >>> node_text = \
    '''<li>
        Bare text
        <section>
            <h3>A</h3>
            B
        </section>
        <section>
            <h3>C</h3>
            <ul>
                <li>D</li>
                <li>E</li>
            </ul>
        </section>
    </li>'''
    >>> node = BeautifulSoup(node_text, 'lxml').li
    >>> meaning_struct_from_li(node)
    {
        'Text': Bare text,
        'A': 'B',
        'C': ['D', 'E'],
    }
    """
    mean = dict()
    global myli
    myli = li
    for sec in li.find_all('section'):
        # extract the section title
        sectitle = sec.h3.get_text()
        # and remove the section
        sec.h3.extract()
        if sec.ul:
            # if the section contains a list, return a list of strings
            mean[sectitle] = [li2.get_text() for li2 in sec.find_all('li')]
        else:
            # if section has no list, return only a string
            mean[sectitle] = sec.get_text()
        sec.extract()

    # remove any figure captions
    for fig in li('figure'):
        fig.extract()

    # cast the remainings to string
    mean["Text"] = li.get_text().strip()
    return mean


def main():
    word = 'Loeffel'
    if len(sys.argv) > 1:
        word = sys.argv[1]
    url = 'http://www.duden.de/rechtschreibung/{word}'.format(word=word)

    # print the searched word formatted as a title
    print(word)
    print("=" * len(word))

    # download the appropriate page
    page = requests.get(url)
    if page.status_code == 404:
        print("not found")
        sys.exit()

    # load the BeautifulSoup object
    soup = BeautifulSoup(page.text, "html.parser")
    nadpis = soup.h1.get_text().replace('\xad', '')

    smpage = dict()
    secs = soup.findAll('section')

    # delete the soft hyphens sometimes found in the h1 html tag
    word = soup.h1.get_text().replace('\xad', '')

    # create a dict mapping section name to the section html node
    smpage = {
        sec.h2.get_text().split()[0]: sec for sec in secs if sec.h2
    }

    # display the gender and part of speech of the word (Wortart)
    try:
        wortart = soup.findAll('strong', {"class": "lexem"})[0].get_text()
        print(wortart)
        print()
    except:
        pass

    # 1. Parse meaning overview section
    meaning_section = smpage[Sections.meaning_overview.value]

    mean_over_array = []
    mean_over_array = recursively_extract(meaning_section, meaning_fun)

    # 2. Parse synonyms section
    # currently unused
    try:
        syn_section = smpage[Sections.synonyms.value]

        syn_array = recursively_extract(syn_section, extract_synonym_from_li)
    except:
        pass

    # 3. Parse meaning section
    # currently unused
    try:
        meanings = smpage[Sections.meanings.value]

        mean_cats = ['Gebrauch', 'Grammatik', 'Text', 'Beispiel', 'Beispiele']

        means_array = recursively_extract(
            meanings, meaning_struct_from_li, maxdepth=2)
    except KeyError:
        means_array = []

    # 4. Parse letters section
    # currently unused

    sec_letters = smpage[Sections.letters.value]

    letters_array = dict()
    for name, ul in zip(["before", "after"], sec_letters.find_all('ul')):
        letters_array[name] = \
            [li.a.get_text() for li in ul.find_all('li')]

    # 5. Parse correct writing section
    # currently unused

    sec_writing = smpage[Sections.correct_writing.value]
    writing_dict = dict()

    sec_writing.header.extract()
    for div in sec_writing.find_all('div'):
        parts = div.get_text().split(':')
        writing_dict[parts[0]] = parts[1].strip()

    # print meaning overview
    print_meaning(mean_over_array)


if __name__ == '__main__':
    main()
