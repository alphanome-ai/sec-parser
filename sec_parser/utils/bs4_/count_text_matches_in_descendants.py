from __future__ import annotations

from typing import Callable

import bs4

from sec_parser.utils.bs4_.get_first_deepest_tag import get_first_deepest_tag
from sec_parser.utils.bs4_.is_unary_tree import is_unary_tree


def count_text_matches_in_descendants(
    bs4_tag: bs4.Tag,
    predicate: Callable[[str], bool],
    *,
    exclude_links: bool | None = None,
) -> int:
    exclude_links = exclude_links if exclude_links is not None else False
    unique_texts = set()
    for child in bs4_tag.descendants:
        if isinstance(child, bs4.Tag):
            if (
                is_unary_tree(child)
                and (deepest_tag := get_first_deepest_tag(child))
                and deepest_tag.name == "a"
            ):
                continue
            text = child.get_text().strip()
            if text and predicate(text):
                unique_texts.add(text)
    return len(unique_texts)
