# -*- coding: utf-8 -*-
"""
Console printing functions
"""
from string import ascii_lowercase

from crayons import white, blue, yellow  # pylint: disable=no-name-in-module


def display_grammar(word, grammar_args):
    """
    Display word grammar forms, corresponds to --grammar switch
    """
    grammar_struct = word.grammar_raw
    if not grammar_struct:
        return

    grammar_tokens = [token.lower() for token in grammar_args.split(',')]

    # filter out grammar forms which do not match provided keys
    tag_columns = []
    value_column = []
    for keys, value in word.grammar_raw:
        lkeys = {key.lower() for key in keys}

        if not (grammar_args == 'ALL' or lkeys.issuperset(grammar_tokens)):
            continue

        reduced_keys = lkeys.difference(grammar_tokens)

        tag_columns.append(list(reduced_keys))
        value_column.append(value)

    # determine the width of the table
    max_keys_count = max(map(len, tag_columns))

    # if provided keys uniquely determine the value(s), display a 1-col table
    if max_keys_count == 0:
        display_table([[value] for value in value_column])
        return

    # otherwise make a nice "| key1 key2 | value |" table
    table = []
    for keys, value in zip(tag_columns, value_column):
        padding = [""] * (max_keys_count - len(keys))
        row = keys + padding + [blue("|")] + [value]
        table.append(row)

    display_table(table)


def display_table(table, cell_spacing=' '):
    """
    Display general table with aligned columns
    """
    cols = list(zip(*table))
    collens = [max(len(word) for word in col) for col in cols]

    for row in table:
        for elem, collen in zip(row, collens):
            print(elem.ljust(collen), end=cell_spacing)
        print()


def display_compounds(word, compound_type='ALL'):
    """
    Print word common compounds
    """
    if compound_type == 'ALL':
        for part_of_speech, compounds in word.compounds.items():
            print(white('# ' + part_of_speech.capitalize(), bold=True))
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
            print(blue("{:>2}. ".format(index)), value, sep='')
        elif isinstance(value, list):
            for index_inner, value_inner in zip(ascii_lowercase, value):
                indent = blue("{:>2}. ".format(index)) if index_inner == 'a' else " " * 4
                print("{} {}".format(indent, blue(index_inner)), blue('. '), value_inner, sep='')
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
    print(yellow(word.title, bold=True))
    print(yellow('=' * len(word.title)))

    if word.phonetic:
        print(white(_('Pronunciation:'), bold=True), word.phonetic)
    if word.alternative_spellings:
        print(white(_('Alternative spellings:'), bold=True), ', '.join(word.alternative_spellings))
    if word.part_of_speech:
        print(white(_('Word type:'), bold=True), word.part_of_speech)
    if word.usage:
        print(white(_('Usage:'), bold=True), word.usage)
    if word.frequency:
        commonness = '{label} {frequency}{max_frequency}'.format(
            label=white(_('Commonness:'), bold=True),
            frequency=word.frequency,
            max_frequency=blue('/5'))
        print(commonness)
    if word.word_separation:
        print('{label} {content}'.format(
            label=white(_('Separation:'), bold=True),
            content=str(blue('|')).join(word.word_separation)))

    if word.meaning_overview:
        print(white(_('Meaning overview:'), bold=True))
        print_tree_of_strings(word.meaning_overview)

    if word.synonyms:
        print(white(_('Synonyms:'), bold=True))
        print_tree_of_strings(word.synonyms)

    if word.compounds:
        print(white(_('Typical compounds:'), bold=True))
        for part_of_speech, words in word.compounds.items():
            print(blue(' - {}:'.format(part_of_speech.capitalize())),
                  ', '.join(words))
