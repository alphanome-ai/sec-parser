from typing import Callable

from sec_parser.processing_steps.abstract_processing_step import AbstractProcessingStep
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import NotYetClassifiedElement


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
            [AbstractSemanticElement],
            bool,
        ],
    ) -> None:
        super().__init__()
        self._contains_single_semantic_element = contains_single_semantic_element

    def _create_composite_element(
        self,
        element: AbstractSemanticElement,
    ) -> AbstractSemanticElement:
        html_tags = element.html_tag.get_children()
        inner_elements: list[AbstractSemanticElement] = []
        for html_tag in html_tags:
            processing_log = element.processing_log.copy()
            inner_element = NotYetClassifiedElement(
                html_tag,
                log_origin=self.__class__.__name__,
                processing_log=processing_log,
            )
            inner_elements.append(inner_element)
        inner_elements = self._process(inner_elements)
        return CompositeSemanticElement.create_from_element(
            element,
            log_origin=self.__class__.__name__,
            inner_elements=inner_elements,
        )

    def _process(
        self,
        elements: list[AbstractSemanticElement],
    ) -> list[AbstractSemanticElement]:
        result = []
        for element in elements:
            contains_single = self._contains_single_semantic_element(element)
            if not contains_single:
                result.append(self._create_composite_element(element))
            else:
                result.append(element)
        return result
