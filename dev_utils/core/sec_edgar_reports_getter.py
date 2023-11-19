from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any

import streamlit as st
from sec_downloader import Downloader

if TYPE_CHECKING:
    from sec_downloader.types import FilingMetadata


@dataclass
class SecEdgarReport:
    metadata: FilingMetadata
    primary_document_html: bytes


class SecEdgarReportsGetter:
    def __init__(self) -> None:
        self._downloader = Downloader("Alphanome.AI", "info@alphanome.ai")

    def get_filing_metadatas(
        self,
        query: str,
    ) -> list[Any]:
        return self._downloader.get_filing_metadatas(query)

    def download_filing(
        self,
        url: str,
    ) -> bytes:
        return self._downloader.download_filing(url=url)

    @classmethod
    def to_dict_list(cls, reports):
        return [cls._rearrange_metadata(asdict(r)) for r in reports]

    @staticmethod
    def _rearrange_metadata(metadata_dict):
        # Convert tickers to string
        if "tickers" in metadata_dict:
            metadata_dict["tickers"] = ", ".join(
                [
                    f"{ticker['exchange']}/{ticker['symbol']}"
                    for ticker in metadata_dict["tickers"]
                ]
            )

        # Define the order of the keys
        keys_order = [
            "company_name",
            "form_type",
            "report_date",
            "cik",
            "accession_number",
        ]
        keys_order += [k for k in metadata_dict if k not in keys_order and k != "items"]
        keys_order.append("items")

        # Rearrange the dictionary
        return {key: metadata_dict[key] for key in keys_order}

    @staticmethod
    def raw_query_to_list(raw_queries: str) -> list[str]:
        return [
            query.strip()
            for line in raw_queries.split("\n")
            for query in line.split(",")
            if query.strip()
        ]


@st.cache_resource()
def get_sec_edgar_reports_getter():
    return SecEdgarReportsGetter()


def get_filing_metadatas(query: str):
    return _get_filing_metadatas(query.strip().upper())


@st.cache_resource()
def _get_filing_metadatas(query: str):
    return get_sec_edgar_reports_getter().get_filing_metadatas(query)
