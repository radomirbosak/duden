# -*- coding: utf-8 -*-
"""
Network requests-related functions
"""

import gzip
from pathlib import Path
import string

import bs4
import requests
from xdg.BaseDirectory import xdg_cache_home

from .word import DudenWord
from .common import clear_text


URL_FORM = 'https://www.duden.de/rechtschreibung/{word}'
SEARCH_URL_FORM = 'https://www.duden.de/suchen/dudenonline/{word}'


def sanitize_word(word):
    """
    Sanitize unicode word for use as filename

    Ascii letters and underscore are kept unchanged.
    Other characters are replaced with "-u{charccode}-" string.
    """
    allowed_chars = string.ascii_letters + '_'

    def sanitize_char(char):
        if char in allowed_chars:
            return char
        return '-u' + str(ord(char)) + '-'
    return ''.join(sanitize_char(char) for char in word)


def cached_response(prefix=''):
    """
    Add `cache=True` keyword argument to a function to allow result caching based on single string
    argument.
    """
    def decorator_itself(func):
        def function_wrapper(cache_key, cache=True, **kwargs):
            cachedir = Path(xdg_cache_home) / 'duden'
            filename = prefix + sanitize_word(cache_key) + '.gz'
            full_path = str(cachedir / filename)

            if cache:
                # try to read from cache
                cachedir.mkdir(parents=True, exist_ok=True)
                try:
                    with gzip.open(full_path, 'rt', encoding='utf8') as f:
                        return f.read()
                except (FileNotFoundError, IOError, EOFError):
                    pass

            result = func(cache_key, **kwargs)

            if cache and result is not None:
                with gzip.open(full_path, 'wt', encoding='utf8') as f:
                    f.write(result)

            return result

        return function_wrapper
    return decorator_itself


@cached_response(prefix='')
def request_word(word):
    """
    Request word page from duden
    """
    url = URL_FORM.format(word=word)
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError as exc:
        raise Exception(_("Connection could not be established. "
                          "Check your internet connection.")) from exc

    if response.status_code == 404:
        return None
    response.raise_for_status()

    return response.text


def get(word, cache=True):
    """
    Load the word 'word' and return the DudenWord instance
    """
    html_content = request_word(word, cache=cache)  # pylint: disable=unexpected-keyword-arg
    if html_content is None:
        return None

    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    return DudenWord(soup)


def get_word_of_the_day():
    """
    Scrapes the word of the day and returns DudenWord instance of it.
    """
    html_content = requests.get("https://www.duden.de").content
    soup = bs4.BeautifulSoup(html_content, "html.parser")
    link = soup.find("a", class_="scene__title-link").get("href")
    word = link.split("/")[-1]  # get word from "/rechtschreibung/word"
    return get(word)


def get_search_link_variants(link_text):
    """
    Lists possible interpretations of link text on search page.

    Used for determining whether a search page entry matches the search term.
    """
    return clear_text(link_text).split(', ')


@cached_response(prefix='search-')
def request_search(word):
    """
    Request search page from duden
    """
    url = SEARCH_URL_FORM.format(word=word)
    return requests.get(url).text


def search(word, exact=True, return_words=True, cache=True):
    """
    Search for a word 'word' in duden
    """
    response_text = request_search(word, cache=cache)  # pylint: disable=unexpected-keyword-arg
    soup = bs4.BeautifulSoup(response_text, 'html.parser')
    definitions = soup.find_all('h2', class_='vignette__title')

    if definitions is None:
        return []

    urlnames = []
    for definition in definitions:
        definition_title = definition.text
        if (not exact) or word in get_search_link_variants(definition_title):
            urlnames.append(definition.find('a')['href'].split('/')[-1])

    if not return_words:
        return urlnames
    return [get(urlname, cache=cache) for urlname in urlnames]
