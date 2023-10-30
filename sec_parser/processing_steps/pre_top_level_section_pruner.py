from sec_parser.processing_steps.abstract_classes.abstract_processing_step import (
    AbstractProcessingStep,
)
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.top_level_section_title import TopLevelSectionTitle


class PreTopLevelSectionPruner(AbstractProcessingStep):
    """
    The PreTopLevelSectionPruner is a processing step designed to eliminate elements
    that are located before the first top-level section of a document.

    For example, consider a SEC EDGAR 10-Q report. This processing step will remove
    all elements that appear before the 'part1item1' section. This means that elements
    such as the title page, table of contents, and others will be eliminated.
    """

    def _process(
        self,
        elements: list[AbstractSemanticElement],
    ) -> list[AbstractSemanticElement]:
        for i, element in enumerate(elements):
            if isinstance(element, TopLevelSectionTitle):
                return elements[i:]
        return elements
