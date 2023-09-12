from __future__ import annotations

import re
from typing import TYPE_CHECKING

import httpx

from sec_parser.data_sources.abstract_sec_data_retriever import (
    AbstractSECDataRetriever,
    DocumentNotFoundError,
)
from sec_parser.data_sources.sec_edgar_types import (
    FORM_SECTIONS,
    SECTION_NAMES,
    DocumentType,
)
from sec_parser.utils.env_var_helpers import get_value_or_env_var

if TYPE_CHECKING:
    from collections.abc import Iterable

    from sec_parser.data_sources.sec_edgar_types import (
        SectionType,
    )


class SecApiIoDataRetriever(AbstractSECDataRetriever):
    SUPPORTED_DOCUMENT_TYPES = frozenset({DocumentType.FORM_10Q})
    API_KEY_ENV_VAR_NAME = "SEC_API_IO_API_KEY"

    def __init__(
        self: SecApiIoDataRetriever,
        *,
        api_key: str | None = None,
        timeout_s: int | None = None,
    ) -> None:
        self._api_key = get_value_or_env_var(api_key, self.API_KEY_ENV_VAR_NAME)
        self._timeout_s = timeout_s or 10

    def _get_html_from_url(
        self: SecApiIoDataRetriever,
        doc_type: DocumentType,
        *,
        url: str,
        sections: Iterable[SectionType] | None = None,
    ) -> str:
        return self._get_sections_html(doc_type, url, sections)

    def _get_latest_html_from_ticker(
        self: SecApiIoDataRetriever,
        doc_type: DocumentType,
        *,
        ticker: str,
        sections: Iterable[SectionType] | None = None,
    ) -> str:
        metadata = self._call_latest_report_metadata_api(
            doc_type,
            key="ticker",
            value=ticker,
        )
        url = metadata["linkToFilingDetails"]
        return self._get_sections_html(doc_type, url, sections)

    def _get_sections_html(
        self: SecApiIoDataRetriever,
        doc_type: DocumentType,
        url: str,
        sections: Iterable[SectionType] | None = None,
    ) -> str:
        html_parts = []
        sections = sections or FORM_SECTIONS[doc_type]
        for section in sections:
            title = SECTION_NAMES[section]
            title = re.sub(r"[^a-zA-Z0-9' ]+", "", title)
            separator_html = (
                "<document-root-section"
                f' id="{section.value}"'
                ' style="display: none;"'
                f' title="{title}">'
                "</document-root-section>"
            )
            html_parts.append(separator_html)
            section_html = self._call_sections_extractor_api(
                url,
                section,
            )
            html_parts.append(section_html)
        return "\n".join(html_parts)

    def _call_sections_extractor_api(
        self: SecApiIoDataRetriever,
        url: str,
        section: SectionType,
    ) -> str:
        params = {
            "url": url,
            "item": section.value,
            "type": "html",
            "token": self._api_key,
        }
        response = httpx.get(
            "https://api.sec-api.io/extractor",
            timeout=self._timeout_s,
            params=params,
        )
        response.raise_for_status()
        return response.text

    def _call_latest_report_metadata_api(
        self: SecApiIoDataRetriever,
        doc_type: DocumentType,
        *,
        key: str,
        value: str,
    ) -> dict:
        key = key.strip().lower()
        value = value.strip().lower()
        query = {
            "query": {
                "query_string": {
                    "query": f'{key}:"{value}" AND formType:"{doc_type.value}"',
                },
            },
            "from": "0",
            "size": "1",
            "sort": [{"filedAt": {"order": "desc"}}],
        }
        client = httpx.Client()
        res = client.post(f"https://api.sec-api.io?token={self._api_key}", json=query)
        res.raise_for_status()
        filings = res.json()["filings"]
        if len(filings) == 0:
            msg = f'no {doc_type.value} found for {key}="{value}"'
            raise DocumentNotFoundError(msg)
        return filings[0]
