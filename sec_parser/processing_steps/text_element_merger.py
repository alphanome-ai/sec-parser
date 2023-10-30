from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.processing_steps.abstract_classes.abstract_element_batch_processing_step import (
    AbstractElementBatchProcessingStep,
)
from sec_parser.processing_steps.abstract_classes.processing_context import (
    ElementProcessingContext,
)
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import TextElement


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
        result: list[AbstractSemanticElement] = []
        batch: list[AbstractSemanticElement] = []
        for element in elements:
            if isinstance(element, TextElement):
                batch.append(element)
                continue
            if batch:
                result.append(self._merge(batch))
                batch = []
            result.append(element)
        if batch:
            result.append(self._merge(batch))

        return result

    @classmethod
    def _merge(
        cls,
        elements: list[AbstractSemanticElement],
    ) -> AbstractSemanticElement:
        if len(elements) == 1:
            return elements[0]

        new_tag = HtmlTag.wrap_tags_in_new_parent(
            "sec-parser-merged-text",
            [e.html_tag for e in elements],
        )
        return TextElement(
            new_tag,
            processing_log=elements[0].processing_log.copy(),
            log_origin=cls.__name__,
        )
