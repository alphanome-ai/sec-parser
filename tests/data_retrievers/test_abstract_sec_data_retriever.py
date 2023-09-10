from __future__ import annotations

from typing import Iterable, Optional
from unittest.mock import Mock, patch

import pytest

from sec_parser._data_retrievers import (
    AbstractSECDataRetriever,
    DocumentType,
    SectionType,
)


class MockSECDataRetriever(AbstractSECDataRetriever):
    def _download_document_impl(
        self,
        *,
        doc_type: DocumentType,
        url: str,
        sections: Optional[Iterable[SectionType]],
    ):
        pass  # Mock implementation


class TestSECDataRetriever:
    def setup_method(self):
        self.retriever = MockSECDataRetriever()

    def test_download_document_unsupported_doc_type(self):
        with pytest.raises(
            ValueError, match="'UNSUPPORTED' is not a valid DocumentType"
        ):
            self.retriever.download_document(
                doc_type="UNSUPPORTED", url="http://example.com"
            )
        with pytest.raises(
            ValueError, match="Unsupported document type: DocumentType._INVALID"
        ):
            self.retriever.download_document(
                doc_type=DocumentType._INVALID, url="http://example.com"
            )

    def test_download_document_invalid_section(self):
        with pytest.raises(
            ValueError, match="'INVALID_SECTION' is not a valid SectionType"
        ):
            self.retriever.download_document(
                doc_type=DocumentType.FORM_10Q,
                url="http://example.com",
                sections=["INVALID_SECTION"],
            )

    @patch.object(
        MockSECDataRetriever, "_download_document_impl", return_value="mocked_data"
    )
    def test_download_document_valid(self, mock_download_impl):
        result = self.retriever.download_document(
            doc_type="10-Q",
            url="http://example.com",
            sections=[SectionType.FORM_10Q_PART1ITEM1],
        )
        assert result == "mocked_data"
        mock_download_impl.assert_called_once_with(
            doc_type=DocumentType.FORM_10Q,
            url="http://example.com",
            sections=(SectionType.FORM_10Q_PART1ITEM1,),
        )

    def test_validate_sections_invalid(self):
        with pytest.raises(ValueError, match="Invalid section"):
            self.retriever._validate_sections(
                doc_type=DocumentType.FORM_10Q, sections=["INVALID_SECTION"]
            )

    def test_validate_sections_valid(self):
        # This test will pass if no exception is raised
        self.retriever._validate_sections(
            doc_type=DocumentType.FORM_10Q, sections=[SectionType.FORM_10Q_PART1ITEM1]
        )
