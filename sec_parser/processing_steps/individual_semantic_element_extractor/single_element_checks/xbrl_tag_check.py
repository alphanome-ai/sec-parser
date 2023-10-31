from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.processing_steps.individual_semantic_element_extractor.single_element_checks.abstract_single_element_check import (
    AbstractSingleElementCheck,
)

if TYPE_CHECKING: # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class XbrlTagCheck(AbstractSingleElementCheck):
    def contains_single_element(self, element: AbstractSemanticElement) -> bool | None:
        if element.html_tag.name.startswith("ix"):
            element.processing_log.add_item(
                log_origin=self.__class__.__name__,
                message=f"Detected XBRL tag {element.html_tag.name}",
            )
            return False
        if element.html_tag.contains_tag("ix:nonnumeric"):
            element.processing_log.add_item(
                log_origin=self.__class__.__name__,
                message=f"Detected XBRL tag ix:nonnumeric in {element.html_tag.name}",
            )
            return False

        return None
