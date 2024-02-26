#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contains the DudenWord class: a parser of duden.de response.
"""

import copy
import gettext
import os

from . import request  # pylint: disable=cyclic-import
from .common import clear_text, recursively_extract

EXPORT_ATTRIBUTES = [
    "name",
    "urlname",
    "title",
    "article",
    "part_of_speech",
    "usage",
    "frequency",
    "word_separation",
    "meaning_overview",
    "origin",
    "grammar_overview",
    "compounds",
    "synonyms",
    "words_before",
    "words_after",
    "phonetic",
    "alternative_spellings",
]

gettext.install("duden", os.path.join(os.path.dirname(__file__), "locale"))


class DudenWord:
    """
    Represents parsed word. Takes a BeautifulSoup object as a constructor argument.

    Example:

        > r = requests.get('https://www.duden.de/rechtschreibung/Hase')
        > soup = bs4.BeautifulSoup(r.text)
        > word = duden.DudenWord(soup)
        > word
        Hase, der (Substantiv, maskulin)
    """

    # pylint: disable=too-many-public-methods
    wordcloud_parts_of_speech = ["substantive", "verben", "adjektive"]

    def __init__(self, soup):
        self.soup = soup
        self._inflection = None

    def __repr__(self):
        return "{} ({})".format(self.title, self.part_of_speech)

    @property
    def title(self):
        """
        The word string with article
        """
        return self.soup.h1.get_text().replace("\xad", "").strip()

    @property
    def name(self):
        """
        Word without article
        """

        # Find span with class "lemma__main"
        title_element = self.soup.find("span", {"class": "lemma__main"})
        if title_element is not None:
            # remove soft hyphens "\xad" and return
            return clear_text(title_element.get_text())

        #  if the title_element does not exist, we fall back to the old method
        if self.part_of_speech is not None and "Substantiv" not in self.part_of_speech:
            return self.title
        if ", " not in self.title:
            return self.title

        name, _ = self.title.split(", ", 1)
        return name

    @property
    def urlname(self):
        """
        Return unique representation of the word used in duden.de urls
        """
        return self.soup.head.find("link", rel="canonical").attrs["href"].split("/")[-1]

    @property
    def revision_url(self):
        """Returns url to this specific word revision"""
        return self.soup.find("input", id="cite-field").attrs["value"]

    @property
    def node_no(self):
        """Returns word node number"""
        return self.revision_url.split("/")[-3]

    @property
    def revision_no(self):
        """Returns word revision number"""
        return self.revision_url.split("/")[-1]

    @property
    def article(self):
        """
        Word article
        """
        # Find span with class "lemma__determiner"
        article_element = self.soup.find("span", {"class": "lemma__determiner"})
        if article_element is not None:
            # remove soft hyphens "\xad" and return
            return clear_text(article_element.get_text())

        #  if the article_element does not exist, we fall back to the old method
        if self.part_of_speech is not None and "Substantiv" not in self.part_of_speech:
            return None
        if ", " not in self.title:
            return None

        _, article = self.title.split(", ", 1)
        return article

    def _find_tuple_dl(self, key, element=None):
        """
        Get value element corresponding to key element containing the text
        provided by the `key` argument
        """
        if element is None:
            element = self.soup.article

        dls = element.find_all("dl", class_="tuple", recursive=False)
        for dl_node in dls:
            label = dl_node.find("dt", class_="tuple__key")
            if key in label.text:
                return dl_node.find("dd", class_="tuple__val")

        return None

    @property
    def part_of_speech(self):
        """
        Return the part of speech
        """
        try:
            pos_element = self._find_tuple_dl("Wortart")
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
            freq_bar = self.soup.find("span", class_="shaft__full")
            return len(freq_bar.text)
        except AttributeError:
            return None

    @property
    def usage(self):
        """
        Return usage context
        """
        try:
            element = self._find_tuple_dl("Gebrauch")
            return element.text
        except AttributeError:
            return None

    @property
    def word_separation(self):
        """
        Return the word separated in a form of a list
        """
        containing_div = self.soup.find("div", id="rechtschreibung")
        sep_element = self._find_tuple_dl("Worttrennung", containing_div)
        if not sep_element:
            return None

        return sep_element.text.split("|")

    @property
    def pronunciation_audio_url(self):
        """
        Return the a url of a audio file for the word pronunciation.
        """
        audio_link = self.soup.select("a.pronunciation-guide__sound")
        if not audio_link:
            return None

        audio_link_href = str(audio_link[0].get("href"))

        return audio_link_href

    @property
    def meaning_overview(self):
        """
        Return the meaning structure, which can be string, list or a dict
        """
        section = self.soup.find("div", id="bedeutung") or self.soup.find(
            "div", id="bedeutungen"
        )
        if section is None:
            return None
        section = copy.copy(section)
        section.header.extract()

        # 1. remove examples
        for dl_node in section.find_all("dl", class_="note"):
            # pylint: disable=condition-evals-to-constant
            if True or dl_node.dt.text == "Beispiele":
                dl_node.extract()

        # 2. remove grammar parts
        for dl_node in section.find_all("dl", class_="tuple"):
            if dl_node.dt.text in ["Grammatik", "Gebrauch"]:
                dl_node.extract()

        # 3. remove pictures
        for node in section.find_all("figure"):
            node.extract()

        return recursively_extract(section, maxdepth=2, exfun=lambda x: x.text.strip())

    @property
    def synonyms(self):
        """
        Return the structure with word synonyms
        """
        section = self.soup.find("div", id="synonyme")
        if section is None:
            return None
        section = copy.copy(section)
        if section.header:
            section.header.extract()
        more_nav = section.find("nav", class_="more")
        if more_nav:
            more_nav.extract()

        return split_synonyms(section.text.strip())

    @property
    def origin(self):
        """
        Return the word origin
        """
        section = self.soup.find("div", id="herkunft")
        if section is None:
            return None

        section = copy.copy(section)
        if section.header:
            section.header.extract()
        return section.text.strip()

    @property
    def grammar_overview(self):
        """
        Return short grammar overview
        """
        section = self.soup.find("div", id="grammatik")
        if section is None:
            return None

        section = copy.copy(section)
        if section.header:
            section.header.extract()
        if section.nav:
            section.nav.extract()
        return section.text.strip() or None

    @property
    def compounds(self):
        """
        Return the typical word compounds
        """
        section = self.soup.find("div", id="kontext")
        if not section:
            return None

        pos_trans = {
            "noun": "substantive",
            "verb": "verben",
            "adj": "adjektive",
        }

        compounds = {}

        cluster_element = section.find("figure", class_="tag-cluster__cluster")
        for a_node in cluster_element.find_all("a"):
            compound_word = a_node.text
            compound_type = pos_trans[a_node.attrs["data-group"]]

            if compound_type not in compounds:
                compounds[compound_type] = []

            compounds[compound_type].append(compound_word)

        compounds_sorted = {}
        for pos in sorted(compounds.keys()):
            compounds_sorted[pos] = sorted(compounds[pos])

        return compounds_sorted

    @property
    def grammar(self):
        """Redirect users to new function"""
        raise RuntimeError("The .grammar property was replaced by .inflection")

    @property
    def grammar_raw(self):
        """Redirect users to new function"""
        raise RuntimeError("The .grammar_raw property was replaced by .inflection")

    @property
    def inflection(self):
        """
        Return word's Inflector object with methods for conjugation and declension

        This property performs a network request, so unless the request is cached, it
        takes a few seconds to return the result.
        """
        if self._inflection is None:
            self._inflection = (
                request.grammar(self.grammar_link) if self.grammar_link else None
            )

        return self._inflection

    @property
    def grammar_link(self):
        """
        Relative url for grammar table page, e.g. "/deklination/substantive/Petersilie"
        """
        section = self.soup.find("div", id="grammatik")
        if not section:
            return None

        link = section.find("a", id="grammatik")
        if not link:
            return None

        return link.attrs["href"]

    @property
    def can_decline(self):
        """Whether word provides declination data"""
        return self.grammar_link.startswith("/deklination")

    @property
    def can_conjugate(self):
        """Whether word provides conjugation data"""
        return self.grammar_link.startswith("/konjugation")

    def export(self):
        """
        Export word's attributes as a dictionary

        Used e.g. for creating test data.
        """
        worddict = {}
        for attribute in EXPORT_ATTRIBUTES:
            worddict[attribute] = getattr(self, attribute, None)
        worddict["inflection"] = self.inflection and self.inflection.data
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
        section = self.soup.find("div", id="block-numero-beforeafterblock-2")
        for group in section.find_all("nav", class_="hookup__group"):
            h3title = group.h3.text
            result[h3title] = []
            for item in group.find_all("li"):
                link = item.a.attrs["href"].split("/")[-1]
                result[h3title].append((clear_text(item.text), link))
        return result

    @property
    def words_before(self):
        """Returns 5 words before this one in duden database"""
        return [name for name, _ in self.before_after_structure["Im Alphabet davor"]]

    @property
    def words_after(self):
        """Returns 5 words after this one in duden database"""
        return [name for name, _ in self.before_after_structure["Im Alphabet danach"]]

    @property
    def phonetic(self):
        """
        Returns pronunciation of the word in phonetic notation.
        See: https://en.wikipedia.org/wiki/International_Phonetic_Alphabet
        """
        ipa = self.soup.find("span", {"class": "ipa"})
        if ipa is not None:
            return ipa.get_text()

        return None

    @property
    def alternative_spellings(self):
        """
        Returns alternate spellings
        """
        alternative_spellings = self.soup.find_all(
            "span", {"class": "lemma__alt-spelling"}
        )
        if alternative_spellings is None:
            return None

        return [spelling.get_text() for spelling in alternative_spellings]


def split_synonyms(text):
    """
    Properly split strings like

    meaning1, (commonly) meaning2; (formal, distant) meaning3
    """
    # split by ',' and ';'
    comma_splits = text.split(",")
    fine_splits = []
    for split in comma_splits:
        fine_splits.extend(split.split(";"))

    # now join back parts which are inside of parentheses
    final_splits = []
    inside_parens = False
    for split in fine_splits:
        if inside_parens:
            final_splits[-1] = final_splits[-1] + "," + split
        else:
            final_splits.append(split)

        if "(" in split and ")" in split:
            inside_parens = split.index("(") > split.index("(")
        elif "(" in split:
            inside_parens = True
        elif ")" in split:
            inside_parens = False

    return [split.strip() for split in final_splits]
