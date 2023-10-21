from typing import Callable

import pytest

from tests._sec_parser_validation_data import traverse_repository_for_reports
from tests.eval.types import ParsedDocumentComponents, Report

reports = list(traverse_repository_for_reports())


@pytest.mark.parametrize(
    "report",
    reports,
    ids=[report.identifier for report in reports],
)
def test_top_level_section_title_classifier(
    report: Report,
    parse: Callable[[Report], ParsedDocumentComponents],
):
    result = parse(report)
    assert result.semantic_elements[1].text == "part i"
