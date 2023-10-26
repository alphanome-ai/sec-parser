from typing import Any, Callable

from sec_parser.processing_engine.create_unclassified_elements import (
    create_unclassified_elements,
)
from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.processing_steps.abstract_processing_step import AbstractProcessingStep
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)


class CompositeElementCreator(AbstractProcessingStep):
    """
    Responsible for aggregating multiple semantic elements wrapped by a single HTML
    element into a CompositeSemanticElement. This ensures structural integrity
    during parsing, which is crucial for accurately reconstructing the original
    HTML document and for semantic analysis where the relationship between elements
    can hold significant meaning.
    """

    def __init__(
        self,
        contains_single_semantic_element: Callable[
            [HtmlTag],
            tuple[bool, dict[str, Any]],
        ],
    ) -> None:
        super().__init__()
        self._contains_single_semantic_element = contains_single_semantic_element

    def _create_composite_element(
        self,
        element: AbstractSemanticElement,
    ) -> AbstractSemanticElement:
        html_tags = element.html_tag.get_children()
        inner_elements = self._process(create_unclassified_elements(html_tags))
        return CompositeSemanticElement.create_from_element(
            element,
            inner_elements=inner_elements,
        )

    def _process(
        self,
        elements: list[AbstractSemanticElement],
    ) -> list[AbstractSemanticElement]:
        result = []
        for element in elements:
            if not self._contains_single_semantic_element(element.html_tag):
                result.append(self._create_composite_element(element))
            else:
                result.append(element)
        return result
