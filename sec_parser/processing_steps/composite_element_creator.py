from sec_parser.processing_steps.abstract_processing_step import AbstractProcessingStep
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)


class CompositeElementCreator(AbstractProcessingStep):
    """
    Responsible for aggregating multiple semantic elements wrapped by a single HTML
    element into a CompositeSemanticElement. This ensures structural integrity
    during parsing, which is crucial for accurately reconstructing the original
    HTML document and for semantic analysis where the relationship between elements
    can hold significant meaning.
    """

    def _process(
        self,
        elements: list[AbstractSemanticElement],
    ) -> list[AbstractSemanticElement]:
        return elements
