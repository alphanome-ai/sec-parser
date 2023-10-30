from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.processing_engine.html_tag_parser import HtmlTagParser
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import NotYetClassifiedElement


def _create_element(tag) -> AbstractSemanticElement:
    if tag.name == "composite":
        inner_tags = tag.get_children()
        return CompositeSemanticElement(
            tag,
            inner_elements=_parse_elements(inner_tags),
        )
    return NotYetClassifiedElement(tag)


def _parse_elements(root_tags: list[HtmlTag]) -> tuple[AbstractSemanticElement, ...]:
    return tuple(_create_element(tag) for tag in root_tags)


def parse_initial_semantic_elements(html: str) -> list[AbstractSemanticElement]:
    html_parser = HtmlTagParser()
    root_tags = html_parser.parse(html.strip())
    return list(_parse_elements(root_tags))
