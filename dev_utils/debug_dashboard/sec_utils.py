from __future__ import annotations

import re
import warnings
from functools import cache

import bs4
from bs4 import XMLParsedAsHTMLWarning

import sec_parser.semantic_elements as se
import sec_parser.semantic_elements.table_element
import sec_parser.semantic_elements.title_element
import sec_parser.semantic_elements.top_level_section_title


def normalize_company_name(name):
    name = name.title()
    name = name.replace("Inc.", "Inc").replace("Corp.", "Corp")
    return name.replace("Inc", "Inc.").replace("Corp", "Corp.")


def generate_bool_list(idx, length):
    """
    >>> generate_bool_list(1, 3)
    [False, True, False]
    >>> generate_bool_list(0, 4)
    [True, False, False, False].
    """
    return [i == idx for i in range(length)]


@cache
def remove_ix_tags(html):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
        soup = bs4.BeautifulSoup(html, "lxml")
    ix_tags = soup.find_all(name=lambda tag: tag and tag.name.startswith("ix:"))
    for tag in ix_tags:
        tag.unwrap()
    return str(soup)


def add_spaces(text):
    return re.sub(r"(\w)([A-Z0-9])", r"\1 \2", text)


def get_emoji_chain(cls: type):
    """
    Walk up the inheritance chain to collect emojis for each parent class.
    Stop when reaching AbstractSemanticElement and only include other
    AbstractSemanticElement parents.
    """
    emojis = []
    for ancestor in cls.mro():
        if ancestor is se.AbstractSemanticElement:
            break  # Stop when reaching AbstractSemanticElement
        if not issubclass(ancestor, se.AbstractSemanticElement):
            continue  # Skip classes that are not descendants of AbstractSemanticElement
        if ancestor is se.AbstractLevelElement:
            continue

        emoji = {
            se.TextElement: "📝",
            sec_parser.semantic_elements.title_element.TitleElement: "🏷️",
            sec_parser.semantic_elements.top_level_section_title.TopLevelSectionTitle: "📚",
            sec_parser.semantic_elements.table_element.TableElement: "📊",
            se.ImageElement: "🖼️",
            se.NotYetClassifiedElement: "🛸",
            se.IrrelevantElement: "🚮",
            se.EmptyElement: "0️⃣",
            se.SupplementaryText: "ℹ️",
        }.get(ancestor, "❓")

        emojis.append(emoji)

    return "".join(reversed(emojis))  # Reverse to start from the root parent


def get_pretty_class_name(element_cls, element=None, *, source: str = ""):
    emoji_chain = get_emoji_chain(element_cls)
    name = add_spaces(element_cls.__name__.replace("Element", "").strip())

    level = ""
    if element and hasattr(element, "level"):
        level = f" | L{element.level}"

    pretty_name = f"{emoji_chain} **{name}**{level}"

    if source:
        pretty_name += f" | {source}"

    return pretty_name


class PassthroughContext:
    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass


def remove_duplicates_retain_order(input_list):
    """This function removes duplicates from a list while retaining the order of elements."""
    return list(dict.fromkeys(input_list))


def clean_user_input(input_list, split_char=None, split_lines=False):
    if split_char and split_lines:
        msg = "Only one of split_char and split_lines can be set."
        raise ValueError(msg)

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
        msg = "Input string must be 18 characters long"
        raise ValueError(msg)
    return s[:10] + "-" + s[10:12] + "-" + s[12:]
