from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.processing_steps.individual_semantic_element_extractor.single_element_checks.abstract_single_element_check import (
    AbstractSingleElementCheck,
)

if TYPE_CHECKING: # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class ImageCheck(AbstractSingleElementCheck):
    def contains_single_element(self, element: AbstractSemanticElement) -> bool | None:
        el_tag = element.html_tag
        if el_tag.name == "img":
            return True

        img_count = el_tag.count_tags("img")

        if img_count > 1:
            msg = f"Detected multiple <img> tags ({img_count})"
            element.processing_log.add_item(
                log_origin=self.__class__.__name__,
                message=msg,
            )
            return False

        if img_count == 1 and el_tag.text:
            element.processing_log.add_item(
                log_origin=self.__class__.__name__,
                message="Detected both text and <img> tag.",
            )
            return False

        return None
