"""
Small module with functions around "grammar" pages like
/deklination/* and
/konjugation/*

The main class is GrammarPage representing the above pages.

Other module-level functions are helper functions to assist the class.
"""
import copy

from .base import DudenPage


class GrammarPage(DudenPage):
    """
    Represents pages like and does a rough parsing of the accordion style HTML elements

    /deklination/{substantive,adjektive}/{word}
    /konjugation/{word}
    """

    @property
    def table_data(self):
        return parse_grammar(self.division("Grammatik"))


def parse_grammar(division):
    return {
        igrp.h3.text: parse_igroup(igrp)
        for igrp in division.div(class_="con-dec__wrapper")
    }


def parse_igroup(igrp):
    return [parse_actable(actable) for actable in igrp.div(class_="accordion-table")]


def parse_actable(actable):
    return [parse_ul(tag_ul) for tag_ul in actable.find_all("ul")]


def parse_ul(tag_ul):
    return [parse_li(tag_li) for tag_li in tag_ul.find_all("li")]


def parse_li(tag_li):
    tag_li = copy.copy(tag_li)
    try:
        tag_li.sup.extract()
    except AttributeError:
        pass
    return tag_li.text
