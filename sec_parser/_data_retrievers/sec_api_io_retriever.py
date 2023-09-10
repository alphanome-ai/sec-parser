from __future__ import annotations

import os
import re
from typing import Iterable

import requests
from frozendict import frozendict

from sec_parser._data_retrievers.abstract_sec_data_retriever import (
    AbstractSECDataRetriever,
    DocumentType,
    SectionType,
)


class InvalidSecEdgarURLError(ValueError):
    pass


class APIKeyNotSetError(ValueError):
    pass


class DocumentTypeNotSupportedError(ValueError):
    pass


class SecApiIoRetriever(AbstractSECDataRetriever):
    _TIMEOUT_S = 10
    _ACCESSION_NUMBER_LEN = 18
    _SUPPORTED_DOC_TYPES = frozenset({DocumentType.FORM_10Q})
    _SECTION_NAMES = frozendict(
        {
            SectionType.FORM_10Q_PART1ITEM1: "Financial Statements",
            SectionType.FORM_10Q_PART1ITEM2: "Management's Discussion and Analysis of Financial Condition and Results of Operations",  # noqa: E501
            SectionType.FORM_10Q_PART1ITEM3: "Quantitative and Qualitative Disclosures About Market Risk",  # noqa: E501
            SectionType.FORM_10Q_PART1ITEM4: "Controls and Procedures",
            SectionType.FORM_10Q_PART2ITEM1: "Legal Proceedings",
            SectionType.FORM_10Q_PART2ITEM1A: "Risk Factors",
            SectionType.FORM_10Q_PART2ITEM2: "Unregistered Sales of Equity Securities and Use of Proceeds",  # noqa: E501
            SectionType.FORM_10Q_PART2ITEM3: "Defaults Upon Senior Securities",
            SectionType.FORM_10Q_PART2ITEM4: "Mine Safety Disclosures",
            SectionType.FORM_10Q_PART2ITEM5: "Other Information",
            SectionType.FORM_10Q_PART2ITEM6: "Exhibits",
        },
    )

    def __init__(self: SecApiIoRetriever, *, api_key: str | None = None) -> None:
        super().__init__()
        self._api_key = api_key or os.environ.get("SEC_API_IO_API_KEY")
        if not self._api_key:
            msg = "sec-api.io api key not set"
            raise APIKeyNotSetError(msg)

    def _download_document_impl(
        self: SecApiIoRetriever,
        *,
        doc_type: DocumentType,
        url: str,
        sections: Iterable[SectionType] | None,
    ) -> str:
        """
        Download HTML of a SEC document of a given type from a provided URL,
        optionally specifying sections to download, otherwise all sections are returned.
        """
        if doc_type not in self._SUPPORTED_DOC_TYPES:
            msg = f"Unsupported document type: {doc_type}"
            raise DocumentTypeNotSupportedError(msg)

        html_parts = []
        sections = sections or self._SECTION_NAMES.keys()
        for section in sections:
            html_parts.append(
                f"""<document-root-section id="{section.value}">"""
                f"""{self._SECTION_NAMES[section]}</document-root-section>""",
            )
            html_parts.append(self._download_html(url, section))
        return "\n".join(html_parts)

    def _download_html(
        self: SecApiIoRetriever,
        filing_details_url: str,
        section: SectionType,
    ) -> str:
        if not self._is_supported_url(filing_details_url):
            msg = "Please use the 'Filing Details' URL by selecting 'Open as HTML'."
            raise InvalidSecEdgarURLError(msg)

        params = {
            "url": filing_details_url,
            "item": section.value,
            "type": "html",
            "token": self._api_key,
        }
        response = requests.get(
            "https://api.sec-api.io/extractor",
            timeout=self._TIMEOUT_S,
            params=params,
        )
        response.raise_for_status()
        return response.text

    @classmethod
    def _is_supported_url(cls: type[SecApiIoRetriever], url: str) -> bool:
        return bool(
            re.match(
                r"https://www\.sec\.gov/Archives/edgar/data/.*",
                url,
            ),
        )
