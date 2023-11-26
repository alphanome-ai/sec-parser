from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from sec_parser.processing_engine.core import Edgar10QParser
from sec_parser.processing_engine.html_tag_parser import HtmlTagParser
from tests._sec_parser_validation_data import ExpectedSection
from tests.generalization.types import ParsedDocumentComponents

if TYPE_CHECKING:  # pragma: no cover
    from tests._sec_parser_validation_data import Report


@pytest.fixture(scope="session")
def parse():
    results = {}

    def _get_result(report: Report):
        if report not in results:
            html_text = report.primary_doc_html_path.read_text()

            expected_sections: list[ExpectedSection] | None = None
            if report.expected_top_level_sections_json_path.exists():
                with report.expected_top_level_sections_json_path.open("r") as file:
                    sections = json.load(file)
                    expected_sections = [
                        ExpectedSection(
                            section_type=section["identifier"],
                            character_count=section["character_count"],
                        )
                        for section in sections
                    ]

            root_tags = HtmlTagParser().parse(html_text)

            elements = Edgar10QParser().parse_from_tags(root_tags)

            results[report] = ParsedDocumentComponents(
                report,
                root_tags,
                elements,
                expected_sections=expected_sections,
            )
        return results[report]

    return _get_result
