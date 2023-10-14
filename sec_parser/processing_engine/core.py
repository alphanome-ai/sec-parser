from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

from sec_parser.processing_engine.html_tag_parser import (
    AbstractHtmlTagParser,
    HtmlTagParser,
)
from sec_parser.processing_steps.highlighted_text_classifier import (
    HighlightedTextClassifier,
)
from sec_parser.processing_steps.image_classifier import ImageClassifier
from sec_parser.processing_steps.table_classifier import TableClassifier
from sec_parser.processing_steps.text_classifier import TextClassifier
from sec_parser.processing_steps.title_classifier import TitleClassifier
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import (
    NotYetClassifiedElement,
    TextElement,
)

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.processing_steps.abstract_processing_step import (
        AbstractProcessingStep,
    )
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class AbstractSemanticElementParser(ABC):
    """
    Responsible for parsing semantic elements from HTML documents.
    It takes raw HTML and returns a list of objects representing semantic elements.

    At a High Level:
    ==================
    1. Extract top-level HTML tags from the document.
    2. Convert them into a list of more specific semantic elements step-by-step.

    Why Focus on Top-Level Tags?
    ============================
    SEC filings typically have a flat HTML structure. This simplifies the
    parsing process, as each top-level HTML tag often directly corresponds
    to a single semantic element. This is different from many websites,
    where HTML tags are usually nested deeply, requiring more complex parsing.

    For Advanced Users:
    ====================
    The parsing process is implemented as a sequence of steps (Pipeline Pattern)
    and allows customization of each step (Strategy Pattern).

    - Pipeline Pattern: Raw HTML tags are processed in a sequential, step-by-step manner
    - Strategy Pattern: You can either replace, remove, or extend any of the existing
      steps with your own or inherited implementation, or you can replace the entire
      pipeline with your own implementation.
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
        steps = self._get_steps()

        root_tags = self._html_tag_parser.parse(html)

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
            ImageClassifier(),
            TableClassifier(types_to_process={NotYetClassifiedElement}),
            TextClassifier(types_to_process={NotYetClassifiedElement}),
            HighlightedTextClassifier(types_to_process={TextElement}),
            TitleClassifier(),
        ]
