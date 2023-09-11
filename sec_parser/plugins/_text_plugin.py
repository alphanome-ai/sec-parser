from sec_parser.entities._html_tag import HtmlTag
from sec_parser.plugins._abstract_parsing_plugin import AbstractParsingPlugin


class TextPlugin(AbstractParsingPlugin):
    def apply(self, _: list[HtmlTag]) -> bool:
        return False
