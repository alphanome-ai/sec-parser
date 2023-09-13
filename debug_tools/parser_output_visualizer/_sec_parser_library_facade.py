import sec_parser as sp
import streamlit as st
from _utils.cache import cache_to_file
from _secapio_api_key_getter import SecapioApiKeyGetter


@cache_to_file(cache_by_keys={"ticker", "doc", "sections"}, cache_dir=".cache")
@st.cache_resource(
    hash_funcs={SecapioApiKeyGetter: lambda _: None},
    experimental_allow_widgets=True,
    show_spinner="Retrieving SEC EDGAR document...",
)
def download_html_from_ticker(
    api_key_getter: SecapioApiKeyGetter,
    *,
    doc: sp.DocumentType | str,
    ticker: str,
    sections: list[sp.SectionType | str] = None
) -> str:
    retriever = sp.SecapioDataRetriever(api_key=api_key_getter.get())
    return retriever.get_latest_html_from_ticker(doc, ticker=ticker, sections=sections)


@cache_to_file(cache_by_keys={"url", "doc", "sections"}, cache_dir=".cache")
@st.cache_resource(
    hash_funcs={SecapioApiKeyGetter: lambda _: None},
    experimental_allow_widgets=True,
    show_spinner="Retrieving SEC EDGAR document...",
)
def download_html_from_url(
    api_key_getter: SecapioApiKeyGetter,
    *,
    doc: sp.DocumentType | str,
    url: str,
    sections: list[sp.SectionType | str] = None
) -> str:
    retriever = sp.SecapioDataRetriever(api_key=api_key_getter.get())
    return retriever.get_html_from_url(doc, url=url, sections=sections)


def get_semantic_elements(html: str) -> list[sp.AbstractSemanticElement]:
    parser = sp.SecParser()
    elements = parser.parse(html)
    return elements


def get_semantic_tree(elements: list[sp.AbstractSemanticElement]) -> sp.SemanticTree:
    tree_builder = sp.TreeBuilder()
    return tree_builder.build(elements)
