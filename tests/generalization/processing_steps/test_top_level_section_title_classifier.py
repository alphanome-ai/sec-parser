from typing import Callable

import pytest

from sec_parser.semantic_elements.semantic_elements import TopLevelSectionTitle
from tests._sec_parser_validation_data import traverse_repository_for_reports
from tests.generalization.types import ParsedDocumentComponents, Report

all_reports = list(traverse_repository_for_reports())
all_report_ids = [report.identifier for report in all_reports]


@pytest.mark.parametrize("report", all_reports, ids=all_report_ids)
def test_top_level_section_title_classifier(
    report: Report,
    parse: Callable[[Report], ParsedDocumentComponents],
):
    parsed_report = parse(report)
    semantic_elements = parsed_report.semantic_elements

    top_level_titles = [
        element
        for element in semantic_elements
        if isinstance(element, TopLevelSectionTitle)
    ]

    assert {title.level for title in top_level_titles}.issubset({0, 1})

    assert top_level_titles[0].level == 0

    level0_titles = [title for title in top_level_titles if title.level == 0]
    assert len(level0_titles) == 2
    part1_idx = top_level_titles.index(level0_titles[0])
    part2_idx = top_level_titles.index(level0_titles[1])

    assert len(top_level_titles[part1_idx + 1 : part2_idx]) == 4
    assert 5 <= len(top_level_titles[part2_idx + 1 :]) <= 7
