from sec_parser.parsing_plugins.abstract_parsing_plugin import AbstractParsingPlugin
from sec_parser.semantic_elements.abstract_semantic_elements import (
    AbstractSemanticElement,
)


class ContentlessPlugin(AbstractParsingPlugin):
    def apply(self, _: list[AbstractSemanticElement]) -> bool:
        return False
