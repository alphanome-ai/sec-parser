import warnings
from pathlib import Path
from typing import Callable

import pytest
import yaml

from sec_parser.semantic_elements.top_level_section_title import TopLevelSectionTitle
from tests._sec_parser_validation_data import Report, traverse_repository_for_reports
from tests.generalization.types import ParsedDocumentComponents

CURRENT_DIR = Path(__file__).parent.resolve()


def _load_yaml_filter(file_path: Path) -> dict:
    with file_path.open("r") as stream:
        return yaml.safe_load(stream)


all_reports = list(traverse_repository_for_reports())
all_accession_numberentifiers = [report.identifier for report in all_reports]
expected_to_pass_accession_numbers = _load_yaml_filter(
    CURRENT_DIR / "test_top_level_section_title_classifier.yaml",
)["accession_numbers"]


@pytest.mark.parametrize("report", all_reports, ids=all_accession_numberentifiers)
def test_top_level_section_title_classifier(
    report: Report,
    parse: Callable[[Report], ParsedDocumentComponents],
):
    if report.accession_number not in expected_to_pass_accession_numbers:
        pytest.skip(f"Skipping {report.identifier}")
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
    msg = f"Duplicate top level section types found, {sections}"
    assert len(sections) == len(set(sections)), msg

    # Check top level 10-Q sections: "part1" and "part2"
    sections0 = [s for s in sections if s.level == 0]
    msg = f"10-Q document should have part1 and part2, but has {[s.section_type.identifier for s in sections0]}"
    assert [s.section_type.identifier for s in sections0] == ["part1", "part2"], msg
    assert sections[0].level == 0
    assert sections[0].section_type.identifier == "part1"

    # Check top level 10-Q sections: "part1item1", "part1item2", etc.
    actual_section_types = [
        s.section_type.identifier for s in sections if s.level == 1 and s.section_type
    ]
    if parsed_report.expected_sections:
        expected_section_types = [
            s.section_type
            for s in parsed_report.expected_sections
            if s.character_count > 0
        ]

        def get_msg() -> str:
            missing = sorted(set(expected_section_types) - set(actual_section_types))
            unexpected = sorted(set(actual_section_types) - set(expected_section_types))

            msg_parts = []
            if len(missing) == len(set(expected_section_types)):
                msg_parts.append('Missing all expected 10-Q "part" sections')
            elif missing:
                msg_parts.append(f"Missing: {missing}")
            if unexpected:
                msg_parts.append(f"Unexpected: {unexpected}")
            if not msg_parts:
                msg_parts.append(
                    f"Actual: {actual_section_types}, Expected: {expected_section_types}",
                )
            return ", ".join(msg_parts)

        assert actual_section_types == expected_section_types, get_msg()
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
