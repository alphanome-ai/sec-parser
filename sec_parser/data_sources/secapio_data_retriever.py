from __future__ import annotations

import re
from typing import TYPE_CHECKING

import httpx

from sec_parser.data_sources.abstract_sec_data_retriever import (
    AbstractSECDataRetriever,
    DocumentTypeNotSupportedError,
)
from sec_parser.data_sources.sec_edgar_enums import (
    FORM_SECTIONS,
    SECTION_NAMES,
    DocumentType,
    SectionType,
)
from sec_parser.exceptions.core_exceptions import (
    SecParserRuntimeError,
    SecParserValueError,
)
from sec_parser.utils.env_var_helpers import get_value_or_env_var

if TYPE_CHECKING:
    from collections.abc import Iterable

ACCESSION_NUMBER_LENGTH = 18


class SecapioApiKeyNotSetError(SecParserValueError):
    pass


class SecapioApiKeyInvalidError(SecParserValueError):
    pass


class SecapioRequestError(SecParserRuntimeError):
    pass


class SecapioDataRetriever(AbstractSECDataRetriever):
    """Retrieves data from sec-api.io API."""

    SUPPORTED_DOCUMENT_TYPES = frozenset({DocumentType.FORM_10Q})
    API_KEY_ENV_VAR_NAME = "SECAPIO_API_KEY"

    def __init__(
        self: SecapioDataRetriever,
        api_key: str | None = None,
        *,
        timeout_s: int | None = None,
    ) -> None:
        self._api_key = get_value_or_env_var(
            api_key,
            self.API_KEY_ENV_VAR_NAME,
            exc=SecapioApiKeyNotSetError,
        )
        self._timeout_s = timeout_s or 10

    def _get_report_html(
        self: SecapioDataRetriever,
        doc_type: DocumentType,
        url: str,
        *,
        sections: Iterable[SectionType] | None = None,
    ) -> str:
        return self._get_sections_html(doc_type, url, sections=sections)

    def retrieve_report_metadata(
        self: SecapioDataRetriever,
        doc_type: DocumentType | str,
        *,
        url: str | None = None,
        latest_from_ticker: str | None = None,
    ) -> dict:
        # Validate arguments
        if not url and not latest_from_ticker:
            msg = "either url or ticker must be provided"
            raise SecParserValueError(msg)
        if url and latest_from_ticker:
            msg = "only one of url or ticker must be provided"
            raise SecParserValueError(msg)
        new_doc_type = (
            DocumentType.from_str(doc_type) if isinstance(doc_type, str) else doc_type
        )
        if new_doc_type not in self.SUPPORTED_DOCUMENT_TYPES:
            msg = f"Document type {doc_type} not supported."
            raise DocumentTypeNotSupportedError(msg)

        # Retrieve metadata
        metadata = None
        if latest_from_ticker:
            metadata = self._call_latest_report_metadata_api(
                new_doc_type,
                key="ticker",
                value=latest_from_ticker,
            )
        if url:
            accession_number = _get_accession_number_from_url(url)
            metadata = self._call_latest_report_metadata_api(
                new_doc_type,
                key="accessionNo",
                value=accession_number,
            )
        if not metadata:
            msg = "metadata is None"
            raise SecParserRuntimeError(msg)
        return metadata

    def _get_sections_html(
        self: SecapioDataRetriever,
        doc_type: DocumentType,
        url: str,
        *,
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
        key = key.strip()
        value = value.strip()
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


def _get_accession_number_from_url(url: str) -> str:
    numbers = re.findall(r"\d+", url)
    s = max(numbers, key=len)
    if len(s) != ACCESSION_NUMBER_LENGTH:
        msg = "Input string must be 18 characters long"
        raise ValueError(msg)
    result = s[:10] + "-" + s[10:12] + "-" + s[12:]
    if not isinstance(result, str):
        msg = f"expected a str, got {type(result)}"
        raise TypeError(msg)
    return result
