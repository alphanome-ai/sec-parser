"""
sec_parsing_entry provides high-level abstractions for parsing SEC documents.
It also serves as library usage examples.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.data_sources.secapio_data_retriever import SecapioDataRetriever
from sec_parser.parsing_engine.sec_parser import SecParser
from sec_parser.semantic_tree.tree_builder import TreeBuilder

if TYPE_CHECKING:
    from sec_parser.data_sources.sec_edgar_enums import DocumentType
    from sec_parser.semantic_tree.semantic_tree import SemanticTree


def parse_latest(
    doc_type: DocumentType | str,
    /,
    *,
    ticker: str,
    secapio_api_key: str | None = None,  # sec-api.io API key
) -> SemanticTree:
    retriever = SecapioDataRetriever(api_key=secapio_api_key)
    metadata = retriever.retrieve_report_metadata(doc_type, latest_from_ticker=ticker)
    url = metadata["linkToFilingDetails"]
    html = retriever.get_report_html(doc_type, url=url)

    parser = SecParser()
    elements = parser.parse(html)

    tree_builder = TreeBuilder()
    return tree_builder.build(elements)
