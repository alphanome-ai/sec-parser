from unittest.mock import patch

import pytest

from sec_parser.data_retrievers.sec_api_io_retriever import (
    APIKeyNotSetError,
    DocumentTypeNotSupportedError,
    InvalidSecEdgarURLError,
    SecApiIoRetriever,
)
from sec_parser.data_retrievers.sec_data_retriever import DocumentType, SectionType


def test_api_key_not_set():
    with pytest.raises(APIKeyNotSetError):
        SecApiIoRetriever(api_key="")


def test_invalid_url():
    retriever = SecApiIoRetriever(api_key="test_key")
    with pytest.raises(InvalidSecEdgarURLError):
        retriever._download_html("invalid_url", SectionType.FORM_10Q_PART1ITEM1)


def test_unsupported_document_type():
    retriever = SecApiIoRetriever(api_key="test_key")
    with pytest.raises(DocumentTypeNotSupportedError):
        retriever._download_document_impl(
            doc_type=DocumentType._INVALID, url="valid_url", sections=None
        )


def test_supported_url():
    retriever = SecApiIoRetriever(api_key="test_key")
    assert retriever._is_supported_url(
        "https://www.sec.gov/Archives/edgar/data/320193/000032019323000077/aapl-20230701.htm"
    )


def test_unsupported_url():
    retriever = SecApiIoRetriever(api_key="test_key")
    assert not retriever._is_supported_url(
        "https://www.sec.gov/ix?doc=/Archives/edgar/data/320193/000032019323000077/aapl-20230701.htm"
    )


@patch("requests.get")
def test_download_document_impl(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "test_response"
    retriever = SecApiIoRetriever(api_key="test_key")
    url = "https://www.sec.gov/Archives/edgar/data/320193/000032019323000077/aapl-20230701.htm"
    doc_type = DocumentType.FORM_10Q
    sections = [SectionType.FORM_10Q_PART1ITEM1, SectionType.FORM_10Q_PART1ITEM2]
    response = retriever._download_document_impl(
        doc_type=doc_type, url=url, sections=sections
    )
    assert response == "\n".join(
        [
            f'<document-root-section id="{section.value}">{SecApiIoRetriever._SECTION_NAMES[section]}</document-root-section>\ntest_response'
            for section in sections
        ]
    )
