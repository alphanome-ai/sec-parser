"""
The parsing_plugins subpackage provides a collection of plugins
designed to work with parser engines from the parsing_engine
subpackage. These plugins carry out specific tasks such as
section identification, title parsing, and text extraction, etc.
"""

from sec_parser.parsing_plugins.abstract_parsing_plugin import AbstractParsingPlugin
from sec_parser.parsing_plugins.footnote_and_bulletpoint_plugin import (
    FootnoteAndBulletpointPlugin,
)
from sec_parser.parsing_plugins.image_plugin import ImagePlugin
from sec_parser.parsing_plugins.root_section_plugin import RootSectionPlugin
from sec_parser.parsing_plugins.table_plugin import TablePlugin
from sec_parser.parsing_plugins.text_plugin import TextPlugin
from sec_parser.parsing_plugins.title_plugin import TitlePlugin

__all__ = [
    "AbstractParsingPlugin",
    "RootSectionPlugin",
    "TextPlugin",
    "TitlePlugin",
    "ImagePlugin",
    "TablePlugin",
    "FootnoteAndBulletpointPlugin",
]
