# -*- coding: utf-8 -*-
"""
Contains functions not directly related to word parsing, but used by the it.
"""
from itertools import cycle

from .constants import PRASENS, PRATERITUM, PERSON_1, PERSON_2, PERSON_3


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
    if node.name in ['ol', 'ul']:
        lilist = node
    else:
        lilist = node.ol or node.ul
    if lilist and maxdepth:
        # apply 'recursively_extract' to every 'li' node found under this node
        return [recursively_extract(li, exfun, maxdepth=(maxdepth - 1))
                for li in lilist.find_all('li', recursive=False)]
    # if this node doesn't contain 'ol' or 'ul' node, return the transformed
    # leaf (using the 'exfun' function)
    return exfun(node)


def clear_text(text):
    """
    Remove soft hyphens anywhere, and heading and trailing spaces.
    """
    return text.replace('\xad', '').strip()


def table_node_to_tagged_cells(table_node):
    """
    Takes a table HTML node and returns the list of table cell strings
    tagged using the table top and left header (optionally using the table
    name found in the upper-leftmost cell).

    The return type is a list of 2-tuples:
    [(tag_set, text), ...]

    where text is a string taken from the cell, and tag_set is a set of
    strings (tags). If e.g. cell in the 3rd row and 2nd column with the
    text 'der Barmherzigkeit', has its top_header tag (1st row, 2nd
    column) 'Singular' and its left_header tag (1st column, 3rd row)
    'Genitiv', the corresponding tuple would look like:
    ({'Singular', 'Genitiv'}, 'der Barmherzigkeit')
    .

    The first row is considered a header row, if it's inside of <thead>
    html tag. The first column is considered a header column if the
    corresponding cells are <th> html nodes.
    """
    # pylint: disable=too-many-locals
    left_header = []
    top_header = None
    table_content = []

    title_element = table_node.h3
    table_name = title_element.text if title_element else ''

    # convert table html node to raw table (list of lists) and optional
    # left and top headers (also lists)
    if table_node.thead:
        all_ths = table_node.thead.find_all(
            'th', class_='wrap-table__flexions-head')
        top_header = [clear_text(t.text) for t in all_ths]

    for row in table_node.tbody.find_all('tr'):
        if row.th:
            th_node = row.th
            rowspan = int(th_node.attrs.get('rowspan', 1))
            left_header.extend([clear_text(row.th.text)] * rowspan)

        tds = row.find_all('td')
        table_content.append([clear_text(td.text) for td in tds])

    # convert left, top, and table headers to sets for easier tagging
    if left_header:
        left_header = [{cell} for cell in left_header]
    else:
        left_header = [set() for _ in table_content]
    if top_header:
        top_header = [{cell} for cell in top_header]
    else:
        top_header = [set() for _ in table_content[0]]
    table_tag = {table_name} if table_name else set()

    if table_name in [PRASENS, PRATERITUM]:
        person_tags = [{PERSON_1}, {PERSON_2}, {PERSON_3}]
    else:
        person_tags = [set(), set(), set()]

    # create a list of tagged strings
    tagged_strings = []
    for row, row_tag, person_tag \
            in zip(table_content, left_header, cycle(person_tags)):
        for cell, col_tag in zip(row, top_header):
            taglist = table_tag \
                .union(row_tag) \
                .union(col_tag) \
                .union(person_tag)
            tagged_strings.append((taglist, cell))
    return tagged_strings
