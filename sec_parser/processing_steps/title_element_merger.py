from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING, cast

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.processing_steps.abstract_classes.abstract_element_batch_processing_step import (
    AbstractElementBatchProcessingStep,
)
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.title_element import TitleElement

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.processing_steps.abstract_classes.processing_context import (
        ElementProcessingContext,
    )


class TitleElementMerger(AbstractElementBatchProcessingStep):
    """
    TitleElementMerger is a processing step that merges adjacent TitleElement instances
    that are on the same line. This addresses issues where section titles are split
    across multiple HTML elements (e.g., "PART I. FINANCI" and "AL INFORMATION").

    Intended to fix weird formatting artifacts, such as:
        <div style="line-height:120%;padding-top:12px;font-size:10pt;">
            <font style="font-family:inherit;font-size:10pt;font-weight:bold;">PART I. FINANCI</font>
        </div>
        <div style="line-height:120%;padding-top:12px;font-size:10pt;">
            <font style="font-family:inherit;font-size:10pt;font-weight:bold;">AL INFORMATION</font>
        </div>
    Notice, how titles are split into multiple divs, even though they form a single title.
    """

    def _process_elements(
        self,
        elements: list[AbstractSemanticElement],
        _: ElementProcessingContext,
    ) -> list[AbstractSemanticElement]:
        result: deque[AbstractSemanticElement | None] = deque(elements)
        batch_indices: list[list[int]] = [[]]

        for i, element in enumerate(elements):
            if isinstance(element, TitleElement):
                if (batch_indices[-1] and
                    self._can_merge_with_batch(element, [elements[j] for j in batch_indices[-1]])):
                    batch_indices[-1].append(i)
                else:
                    if batch_indices[-1]:
                        batch_indices.append([])
                    batch_indices[-1].append(i)
            elif batch_indices[-1]:
                batch_indices.append([])

        for indices in batch_indices:
            if len(indices) <= 1:
                continue
            result[indices[0]] = self._merge(
                cast(
                    list[AbstractSemanticElement],
                    [result[i] for i in indices if result[i]],
                ),
            )
            for i in indices[1:]:
                result[i] = None

        return [element for element in result if element is not None]

    def _can_merge_with_batch(
        self,
        element: TitleElement,
        batch_elements: list[AbstractSemanticElement],
    ) -> bool:
        """Check if a TitleElement can be merged with a batch of elements."""
        if not batch_elements:
            return True

        # All elements in batch must be TitleElements and have same level
        if (not all(isinstance(e, TitleElement) for e in batch_elements) or
            element.level != cast(TitleElement, batch_elements[0]).level):
            return False

        batch_parent = batch_elements[0].html_tag.parent
        element_parent = element.html_tag.parent

        if (batch_parent is None or element_parent is None or
            batch_parent._bs4 != element_parent._bs4):  # noqa: SLF001
            return False

        # Check for separate div titles that shouldn't be merged
        batch_tag = batch_elements[0].html_tag
        element_tag = element.html_tag

        if (batch_tag.name == "div" and element_tag.name == "div" and
            batch_parent._bs4 == element_parent._bs4):  # noqa: SLF001

            batch_text = batch_elements[0].text.strip()
            element_text = element.text.strip()

            if (batch_text and element_text and
                self._are_separate_complete_titles(batch_text, element_text)):
                return False

        return True

    def _are_separate_complete_titles(self, batch_text: str, element_text: str) -> bool:
        """Check if two texts are separate complete titles that shouldn't be merged."""
        min_single_word_length = 5
        batch_is_substantial = len(batch_text.split()) > 1 or len(batch_text) > min_single_word_length
        element_is_substantial = len(element_text.split()) > 1 or len(element_text) > min_single_word_length

        return bool(batch_is_substantial and element_is_substantial and
                   batch_text and batch_text[-1].isalpha() and
                   element_text and element_text[0].isalpha())

    @classmethod
    def _merge(
        cls,
        elements: list[AbstractSemanticElement],
    ) -> AbstractSemanticElement:
        """Merge multiple TitleElements into a single TitleElement."""
        if not elements:
            msg = "Cannot merge empty list of elements"
            raise ValueError(msg)

        if len(elements) == 1:
            return elements[0]

        title_elements = [cast(TitleElement, e) for e in elements]

        new_tag = HtmlTag.wrap_tags_in_new_parent(
            "sec-parser-merged-title",
            [e.html_tag for e in title_elements],
        )
        merged_processing_log = title_elements[0].processing_log.copy()
        # After merging, we retain the processing log of the first element and drop the logs of the others.
        # This is because the merged title element now represents a single entity, and we want to avoid
        # log duplication or confusion about which part of the merged title the logs refer to.
        dropped_logs = [e.processing_log for e in title_elements[1:]]
        if any(dropped_logs):
            merged_processing_log.add_item(
                message=f"Merged {len(title_elements)} TitleElements: {[e.text for e in title_elements]}",
                log_origin=cls.__name__,
            )
        return TitleElement(
            new_tag,
            processing_log=merged_processing_log,
            level=title_elements[0].level,
            log_origin=cls.__name__,
        )
