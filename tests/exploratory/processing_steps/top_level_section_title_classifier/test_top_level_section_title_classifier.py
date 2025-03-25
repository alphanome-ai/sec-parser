import warnings
from pathlib import Path
from typing import Callable

import pytest

from sec_parser.semantic_elements.top_section_title import TopSectionTitle
from sec_parser.semantic_elements.top_section_title_types import FilingSectionsIn10K, FilingSectionsIn10Q
from tests.types import ParsedDocumentComponents, Report
from tests.utils import all_reports, load_yaml_filter

CURRENT_DIR = Path(__file__).parent.resolve()
SHOW_SKIPPED = True


expected_to_pass_accession_numbers = load_yaml_filter(
    CURRENT_DIR / "selected-filings.yaml",
)["accession_numbers"]


def convert_10k_section_to_parser_format(section_number: str) -> str:
    # First determine which part this section belongs to
    section_num = section_number.strip()
    
    # Map sections to their parts
    part_mapping = {
        # Part 1: sections 1-4 and their subsections
        '1': 'part1', '1A': 'part1', '1B': 'part1', '1C': 'part1',
        '2': 'part1', '3': 'part1', '4': 'part1', '4A': 'part1',
        
        # Part 2: sections 5-9 and their subsections
        '5': 'part2', '6': 'part2', '7': 'part2', '7A': 'part2',
        '8': 'part2', '9': 'part2', '9A': 'part2', '9B': 'part2', '9C': 'part2',
        
        # Part 3: sections 10-14
        '10': 'part3', '11': 'part3', '12': 'part3', '13': 'part3', '14': 'part3',
        
        # Part 4: sections 15-16
        '15': 'part4', '16': 'part4'
    }
    
    # Get the part prefix
    part = part_mapping.get(section_num)
    if not part:
        return section_num  # Return unchanged if not found in mapping
        
    # Convert number to lowercase for subsections
    item_num = section_num.lower()
    
    return f"{part}item{item_num}"


def get_expected_parts_for_filing_type(document_type: str) -> list[str]:
    if document_type == "10-K":
        return ["part1", "part2", "part3", "part4"]
    elif document_type == "10-Q":
        return ["part1", "part2"]
    else:
        msg = f"Unsupported document type: {document_type}. Only 10-K and 10-Q are currently supported."
        raise ValueError(msg)


def get_expected_item_ranges_for_filing_type(document_type: str) -> dict[str, tuple[list[str], int, int]]:
    if document_type == "10-K":
        return {
            "part1": (["1", "1A", "1B", "1C", "2", "3", "4", "4A"], 4, 8),
            "part2": (["5", "6", "7", "7A", "8", "9", "9A", "9B", "9C"], 6, 9),
            "part3": (["10", "11", "12", "13", "14"], 4, 5),
            "part4": (["15", "16"], 1, 2),
        }
    elif document_type == "10-Q":
        return {
            "part1": (["1", "2", "3", "4"], 3, 4),
            "part2": (["1", "1a", "2", "3", "4", "5", "6"], 4, 7),
        }
    else:
        msg = f"Unsupported document type: {document_type}. Only 10-K and 10-Q are currently supported."
        raise ValueError(msg)


@pytest.mark.parametrize(
    "report",
    selected_filings := [
        k
        for k in all_reports
        if SHOW_SKIPPED or k.accession_number in expected_to_pass_accession_numbers
    ],
    ids=[k.identifier for k in selected_filings],
)
def test_top_level_section_title_classifier(
    report: Report,
    parse: Callable[[Report], ParsedDocumentComponents],
):
    if report.accession_number not in expected_to_pass_accession_numbers:
        pytest.skip(f"Skipping {report.identifier}")
    
    # Ignore warnings and evaluate results later
    # Used for TTD, as performance improves this should be removed.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Invalid section type for")
        warnings.filterwarnings("ignore", message="Failed to get table metrics")
        parsed_report = parse(report)

    semantic_elements = parsed_report.semantic_elements
    sections = [
        element for element in semantic_elements if isinstance(element, TopSectionTitle)
    ]

    # Sanity checks
    assert len(sections) > 0, "No top level sections found"
    assert {title.level for title in sections}.issubset({0, 1})
    msg = f"Duplicate top level section types found, {sections}"
    assert len(sections) == len(set(sections)), msg

    # Get expected parts for this filing type
    expected_parts = get_expected_parts_for_filing_type(report.document_type)
    
    # Check top level sections
    sections0 = [s for s in sections if s.level == 0]
    msg = f"{report.document_type} document should have {', '.join(expected_parts)}, but has {[s.section_type.identifier for s in sections0]}"
    assert [s.section_type.identifier for s in sections0] == expected_parts, msg
    assert sections[0].level == 0
    assert sections[0].section_type.identifier == "part1"

    # Check part items
    actual_section_types = [
        s.section_type.identifier for s in sections if s.level == 1 and s.section_type
    ]
    
    if parsed_report.expected_sections:
        expected_section_types = [
            s.section_type
            for s in parsed_report.expected_sections
            if s.character_count > 0
        ]

        # Convert expected section types if this is a 10-K
        if report.document_type == "10-K":
            expected_section_types = [
                convert_10k_section_to_parser_format(section_type)
                for section_type in expected_section_types
            ]
        
        missing = sorted(set(expected_section_types) - set(actual_section_types))
        unexpected = sorted(set(actual_section_types) - set(expected_section_types))

        def get_msg() -> str:

            msg_parts = []
            if len(missing) == len(set(expected_section_types)):
                msg_parts.append(f'Missing all expected {report.document_type} "part" sections')
            elif missing:
                msg_parts.append(f"Missing: {missing}")
            if unexpected:
                msg_parts.append(f"Unexpected: {unexpected}")
            if not msg_parts:
                msg_parts.append(
                    f"Actual: {actual_section_types}, Expected: {expected_section_types}",
                )
            return ", ".join(msg_parts)
        
        # More tests can be added relating to missing or extra parts
        assert len(missing) == 0, get_msg()
    else:
        warnings.warn(
            f"No expected sections file found for {report.identifier}. Heuristics will be used.",
            stacklevel=0,
        )

        expected_ranges = get_expected_item_ranges_for_filing_type(report.document_type)

        # Get indices for each part
        part_indices = {}
        for i, section in enumerate(sections0):
            part_indices[section.section_type.identifier] = sections.index(section)

        # Add end index for last part
        for part in expected_parts[:-1]:
            next_part = expected_parts[expected_parts.index(part) + 1]
            part_indices[f"{part}_end"] = part_indices[next_part]
        part_indices[f"{expected_parts[-1]}_end"] = len(sections)

        # Check items in each part
        for part in expected_parts:
            start_idx = part_indices[part]
            end_idx = part_indices[f"{part}_end"]
            part_items = sections[start_idx + 1 : end_idx]
            
            item_numbers, min_items, max_items = expected_ranges[part]
            msg = f"Not a reasonable amount of {report.document_type} {part} items, len={len(part_items)}" + (
                f", {part_items}" if len(part_items) != 0 else ""
            )
            assert min_items <= len(part_items) <= max_items, msg

            # Check that all items found are in the expected format
            actual_items = [s.section_type.identifier for s in part_items]
            expected_item_identifiers = [
                convert_10k_section_to_parser_format(item) if report.document_type == "10-K" else f"{part}item{item}"
                for item in item_numbers
            ]
            invalid_items = [
                item for item in actual_items if item not in expected_item_identifiers
            ]
            assert not invalid_items, f"Found invalid items for {report.document_type} {part}: {invalid_items}. Expected format like: {expected_item_identifiers[0]}"