from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

from sec_parser.processing_engine.html_tag_parser import (
    AbstractHtmlTagParser,
    HtmlTagParser,
)
from sec_parser.processing_steps.footnote_and_bulletpoint_parsing_step import (
    FootnoteAndBulletpointParsingStep,
)
from sec_parser.processing_steps.highlighted_text_parsing_step import (
    HighlightedTextParsingStep,
)
from sec_parser.processing_steps.image_parsing_step import ImageParsingStep
from sec_parser.processing_steps.root_section_parsing_step import RootSectionParsingStep
from sec_parser.processing_steps.table_parsing_step import TableParsingStep
from sec_parser.processing_steps.text_parsing_step import TextParsingStep
from sec_parser.processing_steps.title_parsing_step import TitleParsingStep
from sec_parser.semantic_elements.semantic_elements import (
    TextElement,
    UndeterminedElement,
)

if TYPE_CHECKING:
    from sec_parser.processing_steps.abstract_processing_step import (
        AbstractTransformStep,
    )
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class AbstractSemanticElementParser(ABC):
    @abstractmethod
    def __init__(
        self,
    ) -> None:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def parse(self, html: str) -> list[AbstractSemanticElement]:
        raise NotImplementedError  # pragma: no cover


class SecParser(AbstractSemanticElementParser):
    def __init__(
        self,
        get_steps: Callable[[], list[AbstractTransformStep]] | None = None,
        *,
        root_tag_parser: AbstractHtmlTagParser | None = None,
    ) -> None:
        self.get_steps: Callable = get_steps or self.get_default_steps
        self._root_tag_parser = root_tag_parser or HtmlTagParser()

    def get_default_steps(
        self,
    ) -> list[AbstractTransformStep]:
        return [
            ImageParsingStep(),
            TableParsingStep(process_only={UndeterminedElement}),
            TextParsingStep(process_only={UndeterminedElement}),
            FootnoteAndBulletpointParsingStep(process_only={TextElement}),
            HighlightedTextParsingStep(process_only={TextElement}),
            TitleParsingStep(),
            RootSectionParsingStep(),
        ]

    def parse(self, html: str) -> list[AbstractSemanticElement]:
        steps = self.get_steps()

        # The parsing process is designed to handle the primarily
        # flat HTML structure of SEC filings. Hence, our focus is on
        # the root tags of the HTML document.
        root_tags = self._root_tag_parser.parse(html)

        elements: list[AbstractSemanticElement] = [
            UndeterminedElement(tag, inner_elements=[]) for tag in root_tags
        ]

        for step in steps:
            elements = step.process(elements)

        return elements
