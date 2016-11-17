from string import ascii_lowercase


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

    for i1, m1 in enumerate(tree):
        if type(m1) is str:
            print("{:>2}. {}".format(i1, m1))
        elif type(m1) is list:
            for i2, m2 in zip(ascii_lowercase, m1):
                indent = "{:>2}. ".format(i1) if i2 == 'a' else " " * 4
                print("{} {}. {}".format(indent, i2, m2))
        print()


def clear_text(text):
    return text.replace('\xad', '').strip()
