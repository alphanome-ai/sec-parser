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
from sec_parser.semantic_elements.semantic_elements import (
    IrrelevantElement,
    TextElement,
)

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.processing_steps.abstract_classes.processing_context import (
        ElementProcessingContext,
    )


class TextElementMerger(AbstractElementBatchProcessingStep):
    """
    TextElementMerger is a processing step that merges adjacent text elements
    For example, TextElement(<span></span>) and TextElement(<span></span>)
    into a single TextElement(<span></span><span></span>).

    Intended to fix weird formatting artifacts, such as:
        <ix:nonnumeric contextref="c-1" name="us-gaap:PropertyPlantAndEquipmentTextBlock" id="f-989" escape="true">
            <span style="background-color:#ffffff;color:#000000;font-family:'Arial',sans-serif;font-size:10pt;font-weight:400;line-height:120%">Property and equipment, net, co</span>
            <span style="color:#000000;font-family:'Arial',sans-serif;font-size:10pt;font-weight:400;line-height:120%">nsisted of the following (in millions):</span>
        </ix:nonnumeric>
    Notice, how text is split into two spans, even though it's a single sentence.
    Source: https://www.sec.gov/Archives/edgar/data/1652044/000165204423000094/goog-20230930.htm
    """

    def _process_elements(
        self,
        elements: list[AbstractSemanticElement],
        _: ElementProcessingContext,
    ) -> list[AbstractSemanticElement]:
        result: deque[AbstractSemanticElement | None] = deque(elements)
        batch_indices: list[list[int]] = [[]]

        for i, element in enumerate(elements):
            if isinstance(element, TextElement):
                batch_indices[-1].append(i)
            elif batch_indices[-1] and not isinstance(element, IrrelevantElement):
                batch_indices.append([])

        for indices in batch_indices:
            if len(indices) <= 1:
                continue
            result[indices[0]] = self._merge(
                cast(
                    list[AbstractSemanticElement],
                    # At this point,
                    # there shouldn't be any None
                    # elements in the list anyway
                    [result[i] for i in indices if result[i]],
                ),
            )
            for i in indices[1:]:
                result[i] = None

        return [element for element in result if element is not None]

    @classmethod
    def _merge(
        cls,
        elements: list[AbstractSemanticElement],
    ) -> AbstractSemanticElement:
        new_tag = HtmlTag.wrap_tags_in_new_parent(
            "sec-parser-merged-text",
            [e.html_tag for e in elements],
        )
        return TextElement(
            new_tag,
            processing_log=elements[0].processing_log.copy(),
            log_origin=cls.__name__,
        )
