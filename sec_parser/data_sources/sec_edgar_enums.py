from __future__ import annotations

from enum import Enum

from frozendict import frozendict

from sec_parser.exceptions.core_exceptions import SecParserValueError


class DocumentType(Enum):
    INVALID_DOCUMENT_TYPE = (
        "INVALID"  # Placeholder for invalid or unimplemented document types
    )
    FORM_10Q = "10-Q"

    @staticmethod
    def from_str(s: str) -> DocumentType:
        try:
            return DocumentType(s.strip().upper())
        except ValueError as e:
            msg = f"Invalid document type {s}"
            raise InvalidDocumentTypeError(msg) from e


class SectionType(Enum):
    INVALID_SECTION_TYPE = (
        "INVALID"  # Placeholder for invalid or unimplemented document types
    )
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

    @staticmethod
    def from_str(s: str) -> SectionType:
        try:
            return SectionType(s.strip().lower())
        except ValueError as e:
            msg = f"Invalid section {s}"
            raise InvalidSectionTypeError(msg) from e

    @property
    def name(self) -> str:
        return SECTION_NAMES.get(self, "Unknown Section")


class InvalidDocumentTypeError(SecParserValueError):
    pass


class InvalidSectionTypeError(SecParserValueError):
    pass


FORM_SECTIONS = frozendict(
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

SECTION_NAMES = frozendict(
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
