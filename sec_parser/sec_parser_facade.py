"""
sec_parser_facade offers simplified, high-level functions for parsing SEC filings,
while also serving as an example of library usage.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.processing_engine.sec_parser import SecParser
from sec_parser.semantic_tree.tree_builder import TreeBuilder

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.semantic_tree.semantic_tree import SemanticTree


def parse_10q_from_html(
    html: str,
) -> SemanticTree:
    parser = SecParser()
    elements = parser.parse(html)

    tree_builder = TreeBuilder()
    return tree_builder.build(elements)
