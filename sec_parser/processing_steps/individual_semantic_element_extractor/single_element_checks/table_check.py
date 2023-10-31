from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.processing_steps.individual_semantic_element_extractor.single_element_checks.abstract_single_element_check import (
    AbstractSingleElementCheck,
)

if TYPE_CHECKING: # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class TableCheck(AbstractSingleElementCheck):
    def contains_single_element(self, element: AbstractSemanticElement) -> bool | None:
        el_tag = element.html_tag
        if el_tag.name == "table":
            return True

        table_count = el_tag.count_tags("table")

        if table_count > 1:
            msg = f"Detected multiple <table> tags ({table_count})"
            element.processing_log.add_item(
                log_origin=self.__class__.__name__,
                message=msg,
            )
            return False

        if table_count == 1 and el_tag.has_text_outside_tags("table"):
            element.processing_log.add_item(
                log_origin=self.__class__.__name__,
                message="Detected text outside of the <table> tag.",
            )
            return False

        return None
