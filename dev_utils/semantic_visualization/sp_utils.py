import os
from pathlib import Path

import bs4
import sec_parser as sp

from dev_utils.semantic_visualization.const import *


def get_bg_color_with_element(element: sp.AbstractSemanticElement):
    for element_type, color in COLOR_PAIR:
        if isinstance(element, element_type):
            return color
    return None


def get_bs4_tag(element: sp.AbstractSemanticElement | sp.TreeNode) -> bs4.Tag:
    if isinstance(element, sp.TreeNode):
        return get_bs4_tag(element.semantic_element)

    return getattr(element.html_tag, '_bs4', None)


def get_root_soup(element: bs4.BeautifulSoup | bs4.Tag | sp.HtmlTag | sp.AbstractSemanticElement | sp.TreeNode):
    if isinstance(element, sp.TreeNode):
        return get_root_soup(element.semantic_element)

    if isinstance(element, sp.AbstractSemanticElement):
        root = get_root_soup(element.html_tag)
        return root

    if isinstance(element, sp.HtmlTag):
        return get_root_soup(getattr(element, '_bs4'))

    if element.parent is not None:
        return get_root_soup(element.parent)

    if not isinstance(element, bs4.BeautifulSoup):
        return None

    return element


def assign_extra_style(tag: bs4.Tag, extra_style: dict):
    extra_style_string = '; '.join(f'{key}: {value}' for key, value in extra_style.items())
    org_style = tag.get('style', '')
    new_style = f'{org_style}; {extra_style_string}'
    tag['style'] = new_style


def extract_root_and_tree(html: Path | str):
    if isinstance(html, Path) or os.path.isfile(html):
        with open(html, "r") as fp:
            return extract_root_and_tree(fp.read())

    parser = sp.Edgar10QParser()
    tree_builder = sp.TreeBuilder()
    root_soup = None

    elements = parser.parse(html)

    for element in elements:
        root = get_root_soup(element)
        if root is None:
            continue
        root_soup = root

    semantic_tree = tree_builder.build(elements)

    return root_soup, elements, semantic_tree


def is_table_element(element: sp.AbstractSemanticElement):
    if isinstance(element, sp.TableElement):
        return True
    if element.html_tag.name == 'table':
        return True
    return False


__all__ = [
    "get_bg_color_with_element",
    "get_bs4_tag",
    "get_root_soup",
    "assign_extra_style",
    "extract_root_and_tree",
    "is_table_element",
]
