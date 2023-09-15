from sec_parser.parsing_engine.html_parsers.root_tag_parser import RootTagParser
from sec_parser.semantic_elements.abstract_semantic_elements import (
    AbstractSemanticElement,
)


class SomeElement(AbstractSemanticElement):
    pass


def get_elements_from_html(html: str) -> list[AbstractSemanticElement]:
    html_parser = RootTagParser()
    root_tags = html_parser.parse(html)
    elements: list[AbstractSemanticElement] = [SomeElement(tag) for tag in root_tags]
    return elements
