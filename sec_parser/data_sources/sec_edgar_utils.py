from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.data_sources.sec_edgar_enums import (
    FORM_SECTIONS,
    InvalidDocumentTypeError,
    InvalidSectionTypeError,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from sec_parser.data_sources.sec_edgar_enums import DocumentType, SectionType


def validate_sections(
    doc_type: DocumentType,
    sections: Iterable[SectionType] | None,
) -> None:
    if sections is None:
        return

    if doc_type not in FORM_SECTIONS:
        msg = f"Unsupported document type: {doc_type}"
        raise InvalidDocumentTypeError(msg)

    for section in sections:
        if section not in FORM_SECTIONS[doc_type]:
            msg = f"Unsupported section: {section}"
            raise InvalidSectionTypeError(msg)
