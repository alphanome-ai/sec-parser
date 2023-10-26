from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

from sec_parser.processing_engine.html_tag_parser import (
    AbstractHtmlTagParser,
    HtmlTagParser,
)
from sec_parser.processing_steps.composite_element_creator import (
    CompositeElementCreator,
)
from sec_parser.processing_steps.highlighted_text_classifier import (
    HighlightedTextClassifier,
)
from sec_parser.processing_steps.image_classifier import ImageClassifier
from sec_parser.processing_steps.irrelevant_element_classifier import (
    IrrelevantElementClassifier,
)
from sec_parser.processing_steps.pre_top_level_section_pruner import (
    PreTopLevelSectionPruner,
)
from sec_parser.processing_steps.supplementary_text_classifier import (
    SupplementaryTextClassifier,
)
from sec_parser.processing_steps.table_classifier import TableClassifier
from sec_parser.processing_steps.text_classifier import TextClassifier
from sec_parser.processing_steps.title_classifier import TitleClassifier
from sec_parser.processing_steps.top_level_section_title_classifier import (
    TopLevelSectionTitleClassifier,
)
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.highlighted_text_element import HighlightedTextElement
from sec_parser.semantic_elements.semantic_elements import (
    NotYetClassifiedElement,
    TextElement,
)

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.processing_engine.html_tag import HtmlTag
    from sec_parser.processing_steps.abstract_processing_step import (
        AbstractProcessingStep,
    )
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class AbstractSemanticElementParser(ABC):
    """
    Responsible for parsing semantic elements from HTML documents.
    It takes raw HTML and turns it into a list of objects
    representing semantic elements.

    At a High Level:
    ==================
    1. Extract top-level HTML tags from the document.
    2. Transform these tags into a list of more specific semantic
       elements step-by-step.

    Why Focus on Top-Level Tags?
    ============================
    SEC filings usually have a flat HTML structure, which simplifies the
    parsing process.Each top-level HTML tag often directly corresponds
    to a single semantic element. This is different from many websites
    where HTML tags are nested deeply,requiring more complex parsing.

    For Advanced Users:
    ====================
    The parsing process is implemented as a sequence of steps and allows for
    customization at each step.

    - Pipeline Pattern: Raw HTML tags are processed in a sequential manner.
      The steps follow an ordered, step-by-step approach, akin to a Finite
      State Machine (FSM). Each element transitions through various states
      defined by the sequence of processing steps.

    - Strategy Pattern: Each step is customizable. You can either replace,
      remove, or extend any of the existing steps with your own or
      inherited implementation. Alternatively, you can replace the entire pipeline
      with your own process.
    """

    def __init__(
        self,
        get_steps: Callable[[], list[AbstractProcessingStep]] | None = None,
        *,
        html_tag_parser: AbstractHtmlTagParser | None = None,
    ) -> None:
        self._get_steps = get_steps or self.get_default_steps
        self._html_tag_parser = html_tag_parser or HtmlTagParser()

    @classmethod
    @abstractmethod
    def get_default_steps(cls) -> list[AbstractProcessingStep]:
        raise NotImplementedError  # pragma: no cover

    def parse(
        self,
        html: str,
        *,
        unwrap_elements: bool | None = None,
        include_containers: bool | None = None,
    ) -> list[AbstractSemanticElement]:
        root_tags = self._html_tag_parser.parse(html)
        return self.parse_from_tags(
            root_tags,
            unwrap_elements=unwrap_elements,
            include_containers=include_containers,
        )

    def parse_from_tags(
        self,
        root_tags: list[HtmlTag],
        *,
        unwrap_elements: bool | None = None,
        include_containers: bool | None = None,
    ) -> list[AbstractSemanticElement]:
        steps = self._get_steps()
        elements: list[AbstractSemanticElement] = [
            NotYetClassifiedElement(tag) for tag in root_tags
        ]

        for step in steps:
            elements = step.process(elements)

        if unwrap_elements is False:
            return elements
        return CompositeSemanticElement.unwrap_elements(
            elements,
            include_containers=include_containers,
        )


class Edgar10QParser(AbstractSemanticElementParser):
    """
    The Edgar10QParser class is responsible for parsing SEC EDGAR 10-Q
    quarterly reports. It transforms the HTML documents into a list
    of elements. Each element in this list represents a part of
    the visual structure of the original document.
    """

    @classmethod
    def get_default_steps(cls) -> list[AbstractProcessingStep]:
        return [
            CompositeElementCreator(cls._contains_single_semantic_element),
            ImageClassifier(types_to_process={NotYetClassifiedElement}),
            TableClassifier(types_to_process={NotYetClassifiedElement}),
            TextClassifier(types_to_process={NotYetClassifiedElement}),
            HighlightedTextClassifier(types_to_process={TextElement}),
            SupplementaryTextClassifier(
                types_to_process={TextElement, HighlightedTextElement},
            ),
            TopLevelSectionTitleClassifier(types_to_process={HighlightedTextElement}),
            PreTopLevelSectionPruner(),
            TitleClassifier(types_to_process={HighlightedTextElement}),
            IrrelevantElementClassifier(),
        ]

    @classmethod
    def _contains_single_semantic_element(
        cls,
        element: AbstractSemanticElement,
    ) -> bool:
        el_tag = element.html_tag

        special_tags = ("table", "img")

        # Check if tag itself is a special tag
        if el_tag.name in special_tags:
            return True

        # Check if contains multiple special tags
        special_tag_counts = {name: el_tag.count_tags(name) for name in special_tags}
        for name, count in special_tag_counts.items():
            if count > 1:
                element.processing_log.add_item(
                    log_origin="contains_single_semantic_element",
                    message=f"Detected multiple <{name}> tags ({count})",
                )
                return False

        # Check if contains something else than a special tag
        single_special_tags = [
            name for name, count in special_tag_counts.items() if count == 1
        ]
        if single_special_tags:
            outside_text = element.html_tag.without_tags(single_special_tags).text
            if outside_text:
                element.processing_log.add_item(
                    log_origin="contains_single_semantic_element",
                    message=(
                        f"Detected text outside of the special tags "
                        f"({single_special_tags})."
                    ),
                )
                return False

        return True
