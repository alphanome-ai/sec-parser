from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from sec_parser.exceptions import SecParserValueError
from sec_parser.processing_steps.abstract_classes.abstract_elementwise_processing_step import (
    AbstractElementwiseProcessingStep,
    ElementProcessingContext,
)
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import NotYetClassifiedElement

if TYPE_CHECKING: # pragma: no cover
    from sec_parser.processing_steps.individual_semantic_element_extractor.single_element_checks.abstract_single_element_check import (
        AbstractSingleElementCheck,
    )
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class IndividualSemanticElementExtractor(AbstractElementwiseProcessingStep):
    """
    Responsible for splitting a single HTML representing multiple semantic elements
    into multiple Semantic Element instances with a shared parent instance of
    type CompositeSemanticElement. This ensures structural integrity
    during parsing, which is crucial for accurately reconstructing the original
    HTML document and for semantic analysis where the relationship between elements
    can hold significant meaning.
    """

    def __init__(
        self,
        *,
        types_to_process: set[type[AbstractSemanticElement]] | None = None,
        types_to_exclude: set[type[AbstractSemanticElement]] | None = None,
        get_checks: Callable[[], list[AbstractSingleElementCheck]] | None = None,
    ) -> None:
        super().__init__(
            types_to_process=types_to_process,
            types_to_exclude=types_to_exclude,
        )
        if get_checks is None:
            msg = "get_checks function is not provided"
            raise SecParserValueError(msg)
        self._checks = get_checks()

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

    def _process_element(
        self,
        element: AbstractSemanticElement,
        _: ElementProcessingContext,
    ) -> AbstractSemanticElement:
        contains_single_element = self._contains_single_element(element)
        if not contains_single_element:
            return self._create_composite_element(element)

        return element

    def _contains_single_element(self, element: AbstractSemanticElement) -> bool:
        if not element.html_tag.has_tag_children():
            return True

        for check in self._checks:
            contains_single_element = check.contains_single_element(element)
            if contains_single_element is not None:
                element.processing_log.add_item(
                    log_origin=check.__class__.__name__,
                    message=f"Contains single element: {contains_single_element}",
                )
                return contains_single_element
        return True
