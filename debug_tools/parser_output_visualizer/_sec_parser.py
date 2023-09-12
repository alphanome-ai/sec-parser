import sec_parser as sp

from _utils import cache_to_file

from _ui import (
    SecApiIoApiKeyGetter,
)
import streamlit as st


@cache_to_file(cache_by_keys={"ticker", "doc", "sections"}, cache_dir=".cache")
@st.cache_resource(hash_funcs={SecApiIoApiKeyGetter: lambda _: None})
def download_html_from_ticker(
    api_key_getter: SecApiIoApiKeyGetter,
    *,
    doc: sp.DocumentType | str,
    ticker: str,
    sections: list[sp.SectionType | str] = None
) -> str:
    retriever = sp.SecApiIoDataRetriever(api_key=api_key_getter.get())
    return retriever.get_latest_html_from_ticker(doc, ticker=ticker, sections=sections)


@cache_to_file(cache_by_keys={"doc", "sections"}, cache_dir=".cache")
@st.cache_resource(hash_funcs={SecApiIoApiKeyGetter: lambda _: None})
def download_html_from_url(
    api_key_getter: SecApiIoApiKeyGetter,
    *,
    doc: sp.DocumentType | str,
    url: str,
    sections: list[sp.SectionType | str] = None
) -> str:
    retriever = sp.SecApiIoDataRetriever(api_key=api_key_getter.get())
    return retriever.get_html_from_url(doc, url=url, sections=sections)
