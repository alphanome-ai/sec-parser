from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.processing_steps.composite_element_creator.single_element_checks.abstract_single_element_check import (  # noqa: E501
    AbstractSingleElementCheck,
)

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class XbrlTagCheck(AbstractSingleElementCheck):
    def contains_single_element(self, element: AbstractSemanticElement) -> bool | None:
        if element.html_tag.name.startswith("ix"):
            return False

        return None
