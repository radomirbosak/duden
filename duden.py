#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import bs4
import requests


URL_FORM = 'http://www.duden.de/rechtschreibung/{word}'


class DudenWord():

    def __init__(self, word):
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

    @property
    def part_of_speech(self):
        pos_div = self._section_main_get_node('Wortart:')
        return pos_div.strong.text

    @property
    def frequency(self):
        pos_div = self._section_main_get_node('Häufigkeit:', use_label=False)
        return pos_div.strong.text.count('▮')


def get(word):
    return DudenWord(word)
