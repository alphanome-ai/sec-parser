import warnings
from typing import TYPE_CHECKING, Callable

import pytest

from sec_parser.semantic_elements.top_level_section_title import TopLevelSectionTitle
from tests._sec_parser_validation_data import Report, traverse_repository_for_reports
from tests.generalization.types import ParsedDocumentComponents

all_reports = list(traverse_repository_for_reports())
all_report_ids = [report.identifier for report in all_reports]


@pytest.mark.parametrize("report", all_reports, ids=all_report_ids)
def test_top_level_section_title_classifier(
    report: Report,
    parse: Callable[[Report], ParsedDocumentComponents],
):
    parsed_report = parse(report)
    semantic_elements = parsed_report.semantic_elements
    sections = [
        element
        for element in semantic_elements
        if isinstance(element, TopLevelSectionTitle)
    ]

    # Sanity checks
    assert len(sections) > 0, "No top level sections found"
    assert {title.level for title in sections}.issubset({0, 1})
    msg = f"Duplicate top level section identifiers found, {sections}"
    assert len(sections) == len(set(sections)), msg

    # Check top level 10-Q sections: "part1" and "part2"
    sections0 = [s for s in sections if s.level == 0]
    msg = f"10-Q document should have part1 and part2, but has {[s.identifier for s in sections0]}"
    assert [s.identifier for s in sections0] == ["part1", "part2"], msg
    assert sections[0].level == 0
    assert sections[0].identifier == "part1"

    # Check top level 10-Q sections: "part1item1", "part1item2", etc.
    actual_identifiers = [
        s.identifier for s in sections if s.level == 1 and s.identifier
    ]
    if parsed_report.expected_sections:
        expected_identifiers = [
            s.identifier
            for s in parsed_report.expected_sections
            if s.character_count > 0
        ]

        def get_msg() -> str:
            missing = sorted(set(expected_identifiers) - set(actual_identifiers))
            unexpected = sorted(set(actual_identifiers) - set(expected_identifiers))

            msg_parts = []
            if len(missing) == len(set(expected_identifiers)):
                msg_parts.append('Missing all expected 10-Q "part" sections')
            elif missing:
                msg_parts.append(f"Missing: {missing}")
            if unexpected:
                msg_parts.append(f"Unexpected: {unexpected}")
            if not msg_parts:
                msg_parts.append(
                    f"Actual: {actual_identifiers}, Expected: {expected_identifiers}",
                )
            return ", ".join(msg_parts)

        assert actual_identifiers == expected_identifiers, get_msg()
    else:
        warnings.warn(
            f"No expected sections file found for {report.identifier}. Heuristics will be used.",
            stacklevel=0,
        )
        part1_idx = sections.index(sections0[0])
        part2_idx = sections.index(sections0[1])
        part1_items = sections[part1_idx + 1 : part2_idx]
        msg = f"Not a reasonable amount of 10-Q part1 items, len={len(part1_items)}" + (
            f", {part1_items}" if len(part1_items) != 0 else ""
        )
        assert 1 <= len(part1_items) <= 4, msg
        part2_items = sections[part2_idx + 1 :]
        msg = f"Not a reasonable amount of 10-Q part2 items, len={len(part2_items)}" + (
            f", {part2_items}" if len(part2_items) != 0 else ""
        )
        assert 1 <= len(part2_items) <= 7, msg
