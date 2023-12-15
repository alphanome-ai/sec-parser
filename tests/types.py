from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sec_parser.processing_engine.html_tag import HtmlTag
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


@dataclass(frozen=True)
class Report:
    document_type: str
    company_name: str
    accession_number: str
    report_full_path: Path

    @property
    def expected_elements_json_path(self) -> Path:
        return self.report_full_path / "expected-semantic-elements-list.json"

    @property
    def actual_elements_json_path(self) -> Path:
        return self.report_full_path / "actual-semantic-elements-list.json"

    @property
    def actual_elements_json_diff_path(self) -> Path:
        return self.report_full_path / "actual-semantic-elements-list_diff.txt"

    @property
    def primary_doc_html_path(self) -> Path:
        return self.report_full_path / "primary-document.html"

    @property
    def expected_tables(self) -> Path:
        return self.report_full_path / "expected-tables.json"

    @property
    def expected_structure_and_text(self) -> Path:
        return self.report_full_path / "expected-structure-and-text.json"

    @property
    def actual_structure_and_text(self) -> Path:
        return self.report_full_path / "actual-structure-and-text.json"

    @property
    def actual_structure_and_text_summary(self) -> Path:
        return self.report_full_path / "actual-structure-and-text_summary.json"

    @property
    def expected_top_level_sections_json_path(self) -> Path:
        return self.report_full_path / "expected-top-level-sections.json"

    @property
    def identifier(self) -> str:
        return f"{self.document_type}_{self.company_name}_{self.accession_number}"


@dataclass(frozen=True)
class ExpectedSection:
    section_type: str
    character_count: int


@dataclass
class ParsedDocumentComponents:
    report: Report
    html_tags: list[HtmlTag]
    semantic_elements: list[AbstractSemanticElement]
    expected_sections: list[ExpectedSection] | None = None
