from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from sec_parser.data_retrievers._abstract_sec_data_retriever import (
    AbstractSECDataRetriever,
    DocumentNotFoundError,
)
from sec_parser.data_retrievers._sec_edgar_types import (
    FORM_SECTIONS,
    SECTION_NAMES,
    DocumentType,
)
from sec_parser.utils._env_utils import get_value_or_env_var

if TYPE_CHECKING:
    from collections.abc import Iterable

    from sec_parser.data_retrievers._sec_edgar_types import (
        SectionType,
    )


class SecApiIoRetriever(AbstractSECDataRetriever):
    SUPPORTED_DOCUMENT_TYPES = frozenset({DocumentType.FORM_10Q})
    API_KEY_ENV_VAR_NAME = "SEC_API_IO_API_KEY"

    def __init__(
        self: SecApiIoRetriever,
        *,
        api_key: str | None = None,
        timeout_s: int | None = None,
    ) -> None:
        self._api_key = get_value_or_env_var(api_key, self.API_KEY_ENV_VAR_NAME)
        self._timeout_s = timeout_s or 10

    def _get_html_from_url(
        self: SecApiIoRetriever,
        doc_type: DocumentType,
        *,
        url: str,
        sections: Iterable[SectionType] | None = None,
    ) -> str:
        return self._get_sections_html(doc_type, url, sections)

    def _get_latest_html_from_ticker(
        self: SecApiIoRetriever,
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
        self: SecApiIoRetriever,
        doc_type: DocumentType,
        url: str,
        sections: Iterable[SectionType] | None = None,
    ) -> str:
        html_parts = []
        sections = sections or FORM_SECTIONS[doc_type]
        for section in sections:
            separator_html = (
                f"""<document-root-section id="{section.value}">"""
                f"""{SECTION_NAMES[section]}</document-root-section>"""
            )
            html_parts.append(separator_html)
            section_html = self._call_sections_extractor_api(
                url,
                section,
            )
            html_parts.append(section_html)
        return "\n".join(html_parts)

    def _call_sections_extractor_api(
        self: SecApiIoRetriever,
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
        self: SecApiIoRetriever,
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
