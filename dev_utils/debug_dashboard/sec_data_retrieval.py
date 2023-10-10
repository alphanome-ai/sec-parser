from typing import Optional

import streamlit as st

import sec_parser as sp
from dev_utils.debug_dashboard.cache_utils import cache_to_file


@st.cache_data(
    experimental_allow_widgets=True,
    show_spinner="Retrieving SEC EDGAR document...",
)
@cache_to_file(
    cache_by_keys={"latest_from_ticker", "doc", "url", "sections"},
    cache_dir=".cache/metadata",
)
def get_metadata(
    _secapi_api_key: str,  # prefix _ prevents hashing in st.cache_data
    *,
    doc: sp.DocumentType | str,
    url: str | None = None,
    latest_from_ticker: str | None = None,
) -> str:
    retriever = sp.SecapioDataRetriever(api_key=_secapi_api_key)
    return retriever.retrieve_report_metadata(
        doc,
        url=url,
        latest_from_ticker=latest_from_ticker,
    )


@st.cache_data(
    experimental_allow_widgets=True,
    show_spinner="Retrieving SEC EDGAR document...",
)
@cache_to_file(
    cache_by_keys={"url", "ticker", "doc", "sections"},
    cache_dir=".cache/html",
)
def download_html(
    _secapi_api_key: str,  # prefix _ prevents hashing in st.cache_data
    *,
    ticker: str,  # added just to make the cache write ticker as part of the filename
    doc: sp.DocumentType | str,
    url: str,
    sections: Optional[list[sp.SectionType | str]] = None,
) -> str:
    retriever = sp.SecapioDataRetriever(api_key=_secapi_api_key)
    return retriever.get_report_html(doc, url, sections=sections)


@st.cache_resource
def get_semantic_elements(html: str) -> list[sp.AbstractSemanticElement]:
    parser = sp.SecParser()
    return parser.parse(html)


def get_semantic_tree(elements: list[sp.AbstractSemanticElement]) -> sp.SemanticTree:
    tree_builder = sp.TreeBuilder()
    return tree_builder.build(elements)
    return tree_builder.build(elements)
