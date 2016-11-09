#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from enum import Enum
from string import ascii_lowercase

import requests

from bs4 import BeautifulSoup


class Sections(Enum):
    grammar = "Grammatik"
    pronounciation = "Aussprache"
    correct_writing = "Rechtschreibung"
    meaning_overview = "Bedeutungsübersicht"
    synonyms = "Synonyme"
    meanings = "Bedeutungen,"
    letters = "Blättern"


def recursively_extract(node, exfun, maxdepth=2):
    lilist = node.ol or node.ul
    if lilist and maxdepth:
        return [recursively_extract(li, exfun, maxdepth=(maxdepth - 1))
                for li in lilist.find_all('li', recursive=False)]
    return exfun(node)


def meaning_fun(node):
    return node.get_text().strip()


def print_meaning(meaning):
    for i1, m1 in enumerate(meaning):
        if type(m1) is str:
            print("{:>2}. {}".format(i1, m1))
        elif type(m1) is list:
            for i2, m2 in zip(ascii_lowercase, m1):
                indent = "{:>2}. ".format(i1) if i2 == 'a' else " " * 4
                print("{} {}. {}".format(indent, i2, m2))
        print()


def correct_parenthesis(text):
    newtext = []
    inner = False
    for l in text:
        inner = (l == "(") if (l in "()") else inner
        if inner and l == ";":
            l = ","
        elif not inner and l == ',':
            l = ";"
        newtext.append(l)
    return ''.join(newtext)


def extract_synonym_from_li(node):
    totaltext = correct_parenthesis(node.get_text())
    return [synonym.strip() for synonym in totaltext.split(';')]


def meaning_struct_from_li(li):
    mean = dict()
    global myli
    myli = li
    for sec in li.find_all('section'):
        sectitle = sec.h3.get_text()
        sec.h3.extract()
        if sec.ul:
            mean[sectitle] = [li2.get_text() for li2 in sec.find_all('li')]
        else:
            mean[sectitle] = sec.get_text()
        sec.extract()
    for fig in li('figure'):
        fig.extract()
    mean["Text"] = li.get_text().strip()
    return mean


def main():
    word = 'Loeffel'
    if len(sys.argv) > 1:
        word = sys.argv[1]
    url = 'http://www.duden.de/rechtschreibung/{word}'.format(word=word)

    print(word)
    print("=" * len(word))

    page = requests.get(url)
    if page.status_code == 404:
        print("not found")
        sys.exit()

    soup = BeautifulSoup(page.text, "html.parser")
    nadpis = soup.h1.get_text().replace('\xad', '')

    smpage = dict()
    secs = soup.findAll('section')

    word = soup.h1.get_text().replace('\xad', '')
    smpage = {
        sec.h2.get_text().split()[0]: sec for sec in secs if sec.h2
    }

    try:
        wortart = soup.findAll('strong', {"class": "lexem"})[0].get_text()
        print(wortart)
        print()
    except:
        pass

    # 1. Meaning overview
    meaning_section = smpage[Sections.meaning_overview.value]

    mean_over_array = []
    mean_over_array = recursively_extract(meaning_section, meaning_fun)


    # 2. Synonyms
    syn_section = smpage[Sections.synonyms.value]

    syn_array = recursively_extract(syn_section, extract_synonym_from_li)

    # 3. Meanings
    try:
        meanings = smpage[Sections.meanings.value]

        mean_cats = ['Gebrauch', 'Grammatik', 'Text', 'Beispiel', 'Beispiele']

        means_array = recursively_extract(
            meanings, meaning_struct_from_li, maxdepth=2)
    except KeyError:
        means_array = []

    # 4. Letters

    sec_letters = smpage[Sections.letters.value]

    letters_array = dict()
    for name, ul in zip(["before", "after"], sec_letters.find_all('ul')):
        letters_array[name] = \
            [li.a.get_text() for li in ul.find_all('li')]

    # 5. Correct writing

    sec_writing = smpage[Sections.correct_writing.value]
    writing_dict = dict()

    sec_writing.header.extract()
    for div in sec_writing.find_all('div'):
        parts = div.get_text().split(':')
        writing_dict[parts[0]] = parts[1].strip()

    print_meaning(mean_over_array)


if __name__ == '__main__':
    main()
