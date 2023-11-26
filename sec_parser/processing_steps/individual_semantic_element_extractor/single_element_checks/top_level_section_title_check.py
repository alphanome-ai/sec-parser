from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.processing_steps.individual_semantic_element_extractor.single_element_checks.abstract_single_element_check import (
    AbstractSingleElementCheck,
)
from sec_parser.processing_steps.top_level_section_manager_for_10q import (
    TopLevelSectionManagerFor10Q,
)

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


def _is_match_part_or_item(text: str) -> bool:
    return TopLevelSectionManagerFor10Q.is_match_part_or_item(text)


class TopLevelSectionTitleCheck(AbstractSingleElementCheck):
    def contains_single_element(self, element: AbstractSemanticElement) -> bool | None:
        match_count = element.html_tag.count_text_matches_in_descendants(
            _is_match_part_or_item, exclude_links=True,
        )

        if match_count >= 1:
            return False

        return None
