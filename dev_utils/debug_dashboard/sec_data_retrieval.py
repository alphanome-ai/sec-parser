from pathlib import Path

import streamlit as st
from sec_downloader import DownloadStorage
from sec_edgar_downloader import Downloader

import sec_parser as sp

EDGAR_CLIENT_NAME = "Alphanome.AI"
EDGAR_CLIENT_EMAIL = "info@alphanome.ai"


@st.cache_data(
    experimental_allow_widgets=True,
    show_spinner="Retrieving SEC EDGAR document...",
)
def get_latest_10q_html(
    *,
    ticker: str,
) -> str:
    ticker = ticker.upper().strip()
    assert ticker, "Ticker must not be empty"
    storage = DownloadStorage(filter_pattern="**/*.htm*")
    with storage as path:
        dl = Downloader(EDGAR_CLIENT_NAME, EDGAR_CLIENT_EMAIL, path)
        dl.get("10-Q", ticker, limit=1, download_details=True)
    return storage.get_file_contents()[0].content


@st.cache_resource
def get_semantic_elements(html: str) -> list[sp.AbstractSemanticElement]:
    parser = sp.SecParser()
    return parser.parse(html)


def get_semantic_tree(elements: list[sp.AbstractSemanticElement]) -> sp.SemanticTree:
    tree_builder = sp.TreeBuilder()
    return tree_builder.build(elements)
