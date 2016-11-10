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

    @property
    def part_of_speech(self):
        section = self.soup.find('section', id='block-system-main')
        return section.strong.text

    @property
    def frequency(self):
        section = self.soup.find('section', id='block-system-main')
        return section.find_all('strong')[1].text.count('▮')


def get(word):
    return DudenWord(word)
