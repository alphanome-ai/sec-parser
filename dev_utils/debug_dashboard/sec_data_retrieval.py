import re
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
    if ticker.startswith("_"):
        ticker = ticker.replace("_", "")
        if re.match(r"[A-Z]+", ticker):
            filepath = Path(__file__).resolve().parent / ".cache" / f"{ticker}.html"
            return filepath.read_text()
    storage = DownloadStorage(filter_pattern="**/*.htm*")
    with storage as path:
        dl = Downloader(EDGAR_CLIENT_NAME, EDGAR_CLIENT_EMAIL, path)
        dl.get("10-Q", ticker, limit=1, download_details=True)
    return storage.get_file_contents()[0].content


def get_semantic_elements(html: str) -> list[sp.AbstractSemanticElement]:
    parser = sp.Edgar10QParser()
    return parser.parse(html)


def get_semantic_elements_parallelized(
    html_list: list[str],
) -> list[list[sp.AbstractSemanticElement]]:
    return [get_semantic_elements(html) for html in html_list]


def get_semantic_tree(elements: list[sp.AbstractSemanticElement]) -> sp.SemanticTree:
    tree_builder = sp.TreeBuilder()
    return tree_builder.build(elements)
