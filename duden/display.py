# -*- coding: utf-8 -*-
"""
Console printing functions
"""
from string import ascii_lowercase

import yaml
from crayons import blue, white, yellow  # pylint: disable=no-name-in-module


def display_inflections(word):
    """
    Display word's inflection table
    """
    inf_str = yaml.dump(
        word.inflection.data, indent=2, allow_unicode=True, sort_keys=False
    )
    print(inf_str)


def display_table(table, cell_spacing=" "):
    """
    Display general table with aligned columns
    """
    cols = list(zip(*table))
    collens = [max(len(word) for word in col) for col in cols]

    for row in table:
        for elem, collen in zip(row, collens):
            print(elem.ljust(collen), end=cell_spacing)
        print()


def display_compounds(word, compound_type="ALL"):
    """
    Print word common compounds
    """
    if compound_type == "ALL":
        for part_of_speech, compounds in word.compounds.items():
            print(white("# " + part_of_speech.capitalize(), bold=True))
            print_string_or_list(compounds)
            print()
    else:
        print_string_or_list(word.compounds[compound_type])


def print_tree_of_strings(tree):
    """
    Print a tree of strings up to depth 2

    Args:
        tree: tree of strings

    Example:

    >>> print_tree_of_strings(['Hase', ['Eins', 'Zwei']])
    0. Hase
    <BLANKLINE>
    1.  a. Eins
        b. Zwei
    """
    if isinstance(tree, str):
        print(tree)
        return

    for index, value in enumerate(tree):
        if isinstance(value, str):
            print(blue("{:>2}. ".format(index)), value, sep="")
        elif isinstance(value, list):
            for index_inner, value_inner in zip(ascii_lowercase, value):
                indent = (
                    blue("{:>2}. ".format(index)) if index_inner == "a" else " " * 4
                )
                print(
                    "{} {}".format(indent, blue(index_inner)),
                    blue(". "),
                    value_inner,
                    sep="",
                )
        print()


def print_string_or_list(obj):
    """
    Print string value or all list elements, if of type list
    """
    if isinstance(obj, list):
        for elem in obj:
            print(elem)
    else:
        print(obj)


def describe_word(word):
    """
    Print overall word description
    """
    # pylint: disable=too-many-branches
    print(yellow(word.title, bold=True))
    print(yellow("=" * len(word.title)))

    if word.phonetic:
        print(white(_("Pronunciation:"), bold=True), word.phonetic)
    if word.alternative_spellings:
        print(
            white(_("Alternative spellings:"), bold=True),
            ", ".join(word.alternative_spellings),
        )
    if word.part_of_speech:
        print(white(_("Word type:"), bold=True), word.part_of_speech)
    if word.usage:
        print(white(_("Usage:"), bold=True), word.usage)
    if word.frequency:
        commonness = "{label} {frequency}{max_frequency}".format(
            label=white(_("Commonness:"), bold=True),
            frequency=word.frequency,
            max_frequency=blue("/5"),
        )
        print(commonness)
    if word.word_separation:
        print(
            "{label} {content}".format(
                label=white(_("Separation:"), bold=True),
                content=str(blue("|")).join(word.word_separation),
            )
        )

    if word.origin:
        print(white(_("Origin:"), bold=True), word.origin)

    if word.grammar_overview:
        print(white(_("Grammar:"), bold=True), word.grammar_overview)

    if word.pronunciation_audio_url:
        print(
            "{label} {content}".format(
                label=white(_("Pronunciation audio:"), bold=True),
                content=white(word.pronunciation_audio_url, bold=False),
            )
        )

    if word.meaning_overview:
        print(white(_("Meaning overview:"), bold=True))
        print_tree_of_strings(word.meaning_overview)

    if word.synonyms:
        print(white(_("Synonyms:"), bold=True))
        print_tree_of_strings(word.synonyms)

    if word.compounds:
        print(white(_("Typical compounds:"), bold=True))
        for part_of_speech, words in word.compounds.items():
            print(blue(" - {}:".format(part_of_speech.capitalize())), ", ".join(words))
