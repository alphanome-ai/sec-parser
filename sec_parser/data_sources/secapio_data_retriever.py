from __future__ import annotations

import re
from typing import TYPE_CHECKING

import httpx

from sec_parser.data_sources.abstract_sec_data_retriever import (
    AbstractSECDataRetriever,
)
from sec_parser.data_sources.sec_edgar_enums import (
    FORM_SECTIONS,
    SECTION_NAMES,
    DocumentType,
    SectionType,
)
from sec_parser.utils.env_var_helpers import get_value_or_env_var

if TYPE_CHECKING:
    from collections.abc import Iterable


class SecapioApiKeyNotSetError(Exception):
    pass


class SecapioApiKeyInvalidError(Exception):
    pass


class SecapioRequestError(Exception):
    pass


class SecapioDataRetriever(AbstractSECDataRetriever):
    """Retrieves data from sec-api.io API."""

    SUPPORTED_DOCUMENT_TYPES = frozenset({DocumentType.FORM_10Q})
    API_KEY_ENV_VAR_NAME = "SECAPIO_API_KEY"

    def __init__(
        self: SecapioDataRetriever,
        *,
        api_key: str | None = None,
        timeout_s: int | None = None,
    ) -> None:
        self._api_key = get_value_or_env_var(
            api_key,
            self.API_KEY_ENV_VAR_NAME,
            exc=SecapioApiKeyNotSetError,
        )
        self._timeout_s = timeout_s or 10

    def _get_html_from_url(
        self: SecapioDataRetriever,
        doc_type: DocumentType,
        *,
        url: str,
        sections: Iterable[SectionType] | None = None,
    ) -> str:
        return self._get_sections_html(doc_type, url, sections)

    def _get_latest_html_from_ticker(
        self: SecapioDataRetriever,
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
        self: SecapioDataRetriever,
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
                ' comment="This tag was added by '
                'SecApiIoDataRetriever class based on sec-api.io API"'
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
        self: SecapioDataRetriever,
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
        self: SecapioDataRetriever,
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
        try:
            res = client.post(
                f"https://api.sec-api.io?token={self._api_key}",
                json=query,
            )
            res.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == httpx.codes.FORBIDDEN:
                msg = "Invalid API key."
                raise SecapioApiKeyInvalidError(msg) from e
            msg = f"HTTP Status Error occurred while making the request: {e!s}"
            raise SecapioRequestError(msg) from e
        except httpx.RequestError as e:
            msg = f"An unexpected error occurred while making the request: {e!s}"
            raise SecapioRequestError(msg) from e

        filings = res.json()["filings"]
        if len(filings) == 0:
            msg = f'no {doc_type.value} found for {key}="{value}"'
            raise SecapioRequestError(msg)
        if not isinstance(filings[0], dict):
            msg = f"expected a dict, got {type(filings[0])}"
            raise SecapioRequestError(msg)
        return filings[0]
