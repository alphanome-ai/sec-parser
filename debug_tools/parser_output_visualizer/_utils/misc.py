from __future__ import annotations
import itertools

import re

import bs4
import sec_parser.semantic_elements as se

import collections


def normalize_company_name(name):
    name = name.title()
    name = name.replace("Inc.", "Inc").replace("Corp.", "Corp")
    name = name.replace("Inc", "Inc.").replace("Corp", "Corp.")
    return name


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


def get_pretty_class_name(element_cls, element=None, *, source: str = "", base=False):
    root_subclass = element_cls.get_direct_abstract_semantic_subclass()
    emoji = {
        se.TextElement: "📝",
        se.TitleElement: "🏷️",
        se.RootSectionElement: "📚",
        se.TableElement: "📊",
        se.ImageElement: "🖼️",
        se.UndeterminedElement: "❓",
        se.IrrelevantElement: "🚮",
        se.RootSectionSeparatorElement: "⏸️",
        se.HighlightedElement: "🌟",
    }.get(element_cls if not base else root_subclass, "❓")

    name = add_spaces(element_cls.__name__).replace("Element", "").strip()
    root_subclass_name = (
        add_spaces(root_subclass.__name__).replace("Element", "").strip()
    )
    if base:
        name = root_subclass_name

    level = ""
    if element and hasattr(element, "level") and element.level > 1:
        level = f" (Level {element.level})"

    base_name = ""
    if not base and name != root_subclass_name:
        base_name = f" (type **{root_subclass_name}**)"

    pretty_name = f"{emoji} **{name}{level}**{base_name}"

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


def clean_user_input(input_list, split_char=None, split_lines=False):
    if split_char and split_lines:
        raise ValueError("Only one of split_char and split_lines can be set.")

    if split_char:
        input_list = input_list.split(split_char)
    elif split_lines:
        input_list = input_list.splitlines()

    cleaned_list = []
    for k in input_list:
        stripped_k = k.strip()
        if stripped_k:
            cleaned_list.append(stripped_k)

    return remove_duplicates_retain_order(cleaned_list)


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
