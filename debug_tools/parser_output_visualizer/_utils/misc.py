from __future__ import annotations
import itertools

import re

import bs4
import sec_parser.semantic_elements as se

import collections


def generate_bool_list(idx, length):
    """
    >>> generate_bool_list(1, 3)
    [False, True, False]
    >>> generate_bool_list(0, 4)
    [True, False, False, False]
    """
    return [i == idx for i in range(length)]


def remove_ix_tags(html):
    soup = bs4.BeautifulSoup(html, "lxml")
    ix_tags = soup.find_all(name=lambda tag: tag and tag.name.startswith("ix:"))
    for tag in ix_tags:
        tag.unwrap()
    return str(soup)


def add_spaces(text):
    return re.sub(r"(\w)([A-Z0-9])", r"\1 \2", text)


def get_pretty_class_name(element_cls, element=None, *, source: str = ""):
    emoji = {
        se.UndeterminedElement: "🍃",
        se.TextElement: "📝",
        se.RootSectionElement: "📚",
    }.get(element_cls, "✨")
    level = ""
    if element and hasattr(element, "level") and element.level > 1:
        level = f" (Level {element.level})"
    type_name = add_spaces(element_cls.__name__).replace("Element", "").strip()
    pretty_name = f"{emoji} **{type_name}{level}**"
    if source:
        pretty_name += f" | {source}"
    return pretty_name


class PassthroughContext:
    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass


def remove_duplicates_retain_order(input_list):
    """
    This function removes duplicates from a list while retaining the order of elements.
    """
    return list(dict.fromkeys(input_list))


def get_accession_number_from_url(url):
    numbers = re.findall(r"\d+", url)
    s = max(numbers, key=len)
    if len(s) != 18:
        raise ValueError("Input string must be 18 characters long")
    return s[:10] + "-" + s[10:12] + "-" + s[12:]


def interleave_lists(lists):
    """
    Interleave elements from a list of lists.

    Parameters:
        lists (list): A list of lists to interleave.

    Returns:
        list: A list containing interleaved elements from the input lists.

    Examples:
        >>> interleave_lists([['a', 'b', 'c'], [1, 2], ['q']])
        ['a', 1, 'q', 'b', 2, 'c']

        >>> interleave_lists([[1, 2, 3], ['a', 'b']])
        [1, 'a', 2, 'b', 3]

        >>> interleave_lists([[]])
        []

        >>> interleave_lists([])
        []

        >>> interleave_lists([['a'], ['b'], ['c']])
        ['a', 'b', 'c']
    """
    interleaved = []
    max_length = max(len(lst) for lst in lists) if lists else 0

    for i in range(max_length):
        for lst in lists:
            if i < len(lst):
                interleaved.append(lst[i])

    return interleaved


def circular_zip(*args: List) -> List[Tuple]:
    """
    Zip elements of multiple lists together in a circular fashion.

    If the lengths of the lists are unequal, items from the shorter lists are repeated.

    Args:
        *args: Lists to zip. Each argument should be a list.

    Returns:
        A list of tuples, each containing one element from each list.

    Doctests:
    >>> circular_zip([1, 2, 3], ['a', 'b'])
    [(1, 'a'), (2, 'b'), (3, 'a')]

    >>> circular_zip([1, 2], ['a', 'b', 'c'], ['x', 'y', 'z', 'w'])
    [(1, 'a', 'x'), (2, 'b', 'y'), (1, 'c', 'z'), (2, 'a', 'w')]
    """

    # create a list of cyclic iterators
    cyclic_iters = [
        itertools.cycle(lst) if lst else itertools.repeat(None) for lst in args
    ]

    # get the length of the longest list
    max_length = max(len(lst) for lst in args)

    # zip the arguments and slice the results
    return list(itertools.islice(zip(*cyclic_iters), max_length))
