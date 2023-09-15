# This file contains high-level functionalities,
# commonly used classes, and general exceptions
# for easy access.


from sec_parser.data_sources.sec_edgar_enums import DocumentType, SectionType
from sec_parser.data_sources.secapio_data_retriever import SecapioDataRetriever
from sec_parser.exceptions.core_exceptions import (
    SecParserError,
    SecParserRuntimeError,
    SecParserValueError,
)
from sec_parser.sec_parsing_entry import parse_latest
from sec_parser.semantic_elements.semantic_elements import (
    IrrelevantElement,
    RootSectionElement,
    TitleElement,
    UndeterminedElement,
)
from sec_parser.semantic_tree.tree_builder import TreeBuilder

__all__ = [
    # High-level functionalities
    "parse_latest",
    # Main parser classes
    "SecapioDataRetriever",
    "SecParser",
    "TreeBuilder",
    # Common semantic elements
    "UndeterminedElement",
    "RootSectionElement",
    "TitleElement",
    "TextElement",
    "IrrelevantElement",
    # Common exceptions
    "SecParserError",
    "SecParserRuntimeError",
    "SecParserValueError",
    # Common types
    "DocumentType",
    "SectionType",
]
