"""
The processing_steps subpackage provides a collection of steps
designed to work with parser engines from the parsing_engine
subpackage. These steps carry out specific tasks such as
section identification, title parsing, and text extraction, etc.
"""

from sec_parser.processing_steps.abstract_classes.abstract_elementwise_processing_step import (
    AbstractElementwiseProcessingStep,
)
from sec_parser.processing_steps.abstract_classes.abstract_processing_step import (
    AbstractProcessingStep,
)
from sec_parser.processing_steps.empty_element_classifier import EmptyElementClassifier
from sec_parser.processing_steps.highlighted_text_classifier import (
    HighlightedTextClassifier,
)
from sec_parser.processing_steps.image_classifier import ImageClassifier
from sec_parser.processing_steps.individual_semantic_element_extractor.individual_semantic_element_extractor import (
    IndividualSemanticElementExtractor,
)
from sec_parser.processing_steps.individual_semantic_element_extractor.single_element_checks.image_check import (
    ImageCheck,
)
from sec_parser.processing_steps.individual_semantic_element_extractor.single_element_checks.table_check import (
    TableCheck,
)
from sec_parser.processing_steps.individual_semantic_element_extractor.single_element_checks.top_section_title_check import (
    TopSectionTitleCheck,
)
from sec_parser.processing_steps.individual_semantic_element_extractor.single_element_checks.xbrl_tag_check import (
    XbrlTagCheck,
)
from sec_parser.processing_steps.introductory_section_classifier import (
    IntroductorySectionElementClassifier,
)
from sec_parser.processing_steps.page_header_classifier import PageHeaderClassifier
from sec_parser.processing_steps.page_number_classifier import PageNumberClassifier
from sec_parser.processing_steps.supplementary_text_classifier import (
    SupplementaryTextClassifier,
)
from sec_parser.processing_steps.table_classifier import TableClassifier
from sec_parser.processing_steps.table_of_contents_classifier import (
    TableOfContentsClassifier,
)
from sec_parser.processing_steps.text_classifier import TextClassifier
from sec_parser.processing_steps.text_element_merger import TextElementMerger
from sec_parser.processing_steps.title_classifier import TitleClassifier
from sec_parser.processing_steps.top_section_manager_for_10q import (
    TopSectionManagerFor10Q,
)

__all__ = [
    "AbstractProcessingStep",
    "AbstractElementwiseProcessingStep",
    "EmptyElementClassifier",
    "HighlightedTextClassifier",
    "ImageCheck",
    "ImageClassifier",
    "IndividualSemanticElementExtractor",
    "IntroductorySectionElementClassifier",
    "PageHeaderClassifier",
    "PageNumberClassifier",
    "SupplementaryTextClassifier",
    "TableCheck",
    "TableClassifier",
    "TableOfContentsClassifier",
    "TextClassifier",
    "TextElementMerger",
    "TitleClassifier",
    "TopSectionManagerFor10Q",
    "TopSectionTitleCheck",
    "XbrlTagCheck",
]
