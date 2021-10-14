# -*- coding: utf-8 -*-
"""
CLI related functions
"""

import argparse
import sys

from crayons import white, blue, red  # pylint: disable=no-name-in-module
import yaml

from .__version__ import __version__
from .search import get, search
from .display import (display_grammar, display_compounds, print_tree_of_strings,
                      print_string_or_list, describe_word)


def display_word(word, args):
    """
    Display word attribute or general description, based on commandline arguments
    """
    # pylint: disable=too-many-branches
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
            display_compounds(word, args.compounds)
    elif args.phonetic:
        if word.phonetic:
            print(word.phonetic)
    elif args.alternative_spellings:
        if word.alternative_spellings:
            for spelling in word.alternative_spellings:
                print(spelling)
    elif args.grammar:
        display_grammar(word, args.grammar)
    elif args.export:
        yaml_string = yaml.dump(word.export(),
                                sort_keys=False, allow_unicode=True)
        print(yaml_string, end='')
    elif args.words_before:
        print_string_or_list(word.words_before)
    elif args.words_after:
        print_string_or_list(word.words_after)
    else:
        # print the description
        describe_word(word)


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
    parser.add_argument('--export', action='store_true',
                        help=_('export parsed word attributes in yaml format'))
    parser.add_argument('--words-before', action='store_true',
                        help=_('list 5 words before this one'))
    parser.add_argument('--words-after', action='store_true',
                        help=_('list 5 words after this one'))

    parser.add_argument('-r', '--result', type=int,
                        help=_('display n-th (starting from 1) result in case '
                               'of multiple words matching the input'))
    parser.add_argument('--fuzzy', action='store_true',
                        help=_('enable fuzzy word matching'))
    parser.add_argument('--no-cache', action='store_false', dest='cache',
                        help=_('do not cache retrieved words'))

    parser.add_argument('-V', '--version', action='store_true',
                        help=_('print program version'))
    parser.add_argument('--phonetic', action='store_true',
                        help=_('display pronunciation'))
    parser.add_argument('--alternative-spellings', action='store_true',
                        help=_('display alternative spellings'))

    return parser.parse_args()


def main():
    """
    Take the first CLI argument and describe the corresponding word
    """

    # handle the --version switch
    if '--version' in sys.argv or '-V' in sys.argv:
        print('duden ' + __version__)
        sys.exit(0)

    # parse normal arguments
    args = parse_args()

    # search all words matching the string
    words = search(args.word, return_words=False, exact=not args.fuzzy,
                   cache=args.cache)

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
        word = get(word_url_suffix, cache=args.cache)
    except Exception as exception:  # pylint: disable=broad-except
        print(red(exception))
        sys.exit(1)

    display_word(word, args)


if __name__ == '__main__':
    main()
