from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Iterable

from frozendict import frozendict


class DocumentType(Enum):
    _INVALID = "INVALID"
    FORM_10Q = "10-Q"


class SectionType(Enum):
    _INVALID = "INVALID"
    FORM_10Q_PART1ITEM1 = "part1item1"
    FORM_10Q_PART1ITEM2 = "part1item2"
    FORM_10Q_PART1ITEM3 = "part1item3"
    FORM_10Q_PART1ITEM4 = "part1item4"
    FORM_10Q_PART2ITEM1 = "part2item1"
    FORM_10Q_PART2ITEM1A = "part2item1a"
    FORM_10Q_PART2ITEM2 = "part2item2"
    FORM_10Q_PART2ITEM3 = "part2item3"
    FORM_10Q_PART2ITEM4 = "part2item4"
    FORM_10Q_PART2ITEM5 = "part2item5"
    FORM_10Q_PART2ITEM6 = "part2item6"


class SECDataRetriever(ABC):
    _doc_type_to_section_type = frozendict(
        {
            DocumentType.FORM_10Q: [
                SectionType.FORM_10Q_PART1ITEM1,
                SectionType.FORM_10Q_PART1ITEM2,
                SectionType.FORM_10Q_PART1ITEM3,
                SectionType.FORM_10Q_PART1ITEM4,
                SectionType.FORM_10Q_PART2ITEM1,
                SectionType.FORM_10Q_PART2ITEM1A,
                SectionType.FORM_10Q_PART2ITEM2,
                SectionType.FORM_10Q_PART2ITEM3,
                SectionType.FORM_10Q_PART2ITEM4,
                SectionType.FORM_10Q_PART2ITEM5,
                SectionType.FORM_10Q_PART2ITEM6,
            ],
        },
    )

    def download_document(
        self: SECDataRetriever,
        *,
        doc_type: DocumentType | str,
        url: str,
        sections: Iterable[SectionType | str] | None = None,
    ) -> str:
        """
        Download HTML of a SEC document of a given type from a provided URL,
        optionally specifying sections to download, otherwise all sections are returned.
        """
        doc_type = DocumentType(doc_type) if isinstance(doc_type, str) else doc_type
        if doc_type not in self._doc_type_to_section_type:
            msg = f"Unsupported document type: {doc_type}"
            raise ValueError(msg)

        if sections is not None:
            sections = tuple(
                SectionType(section) if isinstance(section, str) else section
                for section in sections
            )
            self._validate_sections(doc_type=doc_type, sections=sections)

        return self._download_document_impl(
            doc_type=doc_type,
            url=url,
            sections=sections,
        )

    @abstractmethod
    def _download_document_impl(
        self: SECDataRetriever,
        *,
        doc_type: DocumentType,
        url: str,
        sections: Iterable[SectionType] | None,
    ) -> str:
        """Implement the logic to download the document in subclasses."""
        raise NotImplementedError  # pragma: no cover

    def _validate_sections(
        self: SECDataRetriever,
        *,
        doc_type: DocumentType,
        sections: Iterable[SectionType | str],
    ) -> None:
        valid_sections = self._doc_type_to_section_type[doc_type]
        for section in sections:
            if section not in valid_sections:
                msg = f"Invalid section {section} for document type {doc_type}"
                raise ValueError(
                    msg,
                )
