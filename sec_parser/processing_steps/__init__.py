"""
The processing_steps subpackage provides a collection of steps
designed to work with parser engines from the parsing_engine
subpackage. These steps carry out specific tasks such as
section identification, title parsing, and text extraction, etc.
"""

from sec_parser.processing_steps.abstract_elementwise_processing_step import (
    AbstractElementwiseProcessingStep,
)
from sec_parser.processing_steps.abstract_processing_step import AbstractProcessingStep
from sec_parser.processing_steps.composite_element_creator import (
    CompositeElementCreator,
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

__all__ = [
    "AbstractProcessingStep",
    "AbstractElementwiseProcessingStep",
    "TextClassifier",
    "TitleClassifier",
    "ImageClassifier",
    "TableClassifier",
    "CompositeElementCreator",
    "SupplementaryTextClassifier",
    "TopLevelSectionTitleClassifier",
    "IrrelevantElementClassifier",
    "PreTopLevelSectionPruner",
]
