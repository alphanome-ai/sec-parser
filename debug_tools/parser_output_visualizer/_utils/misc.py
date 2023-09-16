from __future__ import annotations

import re

import bs4
import sec_parser.semantic_elements as se


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


def get_pretty_class_name(element_cls, element=None):
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
    return pretty_name
