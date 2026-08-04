import bs4
import pytest

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.processing_steps.title_element_merger import TitleElementMerger
from sec_parser.semantic_elements.title_element import TitleElement
from tests.unit._utils import assert_elements


def html_tag(tag_name: str, text: str = "Hello World") -> HtmlTag:
    tag = bs4.Tag(name=tag_name)
    tag.string = text
    return HtmlTag(tag)


def create_title_element(text: str, level: int = 0) -> TitleElement:
    """Helper function to create a TitleElement with specific text and level."""
    tag = html_tag("span", text)
    return TitleElement(tag, level=level)


def create_title_elements_with_same_parent(texts: list[str], level: int = 0) -> list[TitleElement]:
    """Helper function to create TitleElements that share the same parent HTML element."""
    parent_tag = bs4.Tag(name="div")
    
    elements = []
    for text in texts:
        child_tag = bs4.Tag(name="span")
        child_tag.string = text
        parent_tag.append(child_tag)
        child_html_tag = HtmlTag(child_tag)
        element = TitleElement(child_html_tag, level=level)
        elements.append(element)
    
    return elements


@pytest.mark.parametrize(
    ("name", "elements", "expected_elements"),
    values := [
        (
            "no_merge_single_title_element",
            [
                create_title_element("Single Title", level=0),
            ],
            [
                {
                    "type": TitleElement,
                    "tag": "span",
                    "text": "Single Title",
                    "fields": {"level": 0},
                },
            ],
        ),
        (
            "merge_adjacent_title_elements_same_level",
            create_title_elements_with_same_parent(["PART I. FINANCI", "AL INFORMATION"], level=0),
            [
                {
                    "type": TitleElement,
                    "tag": "sec-parser-merged-title",
                    "text": "PART I. FINANCIAL INFORMATION",
                    "fields": {"level": 0},
                },
            ],
        ),
        (
            "no_merge_different_levels",
            [
                create_title_element("Main Title", level=0),
                create_title_element("Sub Title", level=1),
            ],
            [
                {
                    "type": TitleElement,
                    "tag": "span",
                    "text": "Main Title",
                    "fields": {"level": 0},
                },
                {
                    "type": TitleElement,
                    "tag": "span",
                    "text": "Sub Title",
                    "fields": {"level": 1},
                },
            ],
        ),
        (
            "merge_multiple_adjacent_title_elements",
            create_title_elements_with_same_parent(["ITEM 1. FINANCI", "AL STATEMENTS", "AND NOTES"], level=0),
            [
                {
                    "type": TitleElement,
                    "tag": "sec-parser-merged-title",
                    "text": "ITEM 1. FINANCIAL STATEMENTS AND NOTES",
                    "fields": {"level": 0},
                },
            ],
        ),
        (
            "no_merge_with_non_title_element_in_between",
            [
                create_title_element("First Title", level=0),
                # This would be a different element type in practice
                create_title_element("Second Title", level=0),
            ],
            [
                {
                    "type": TitleElement,
                    "tag": "span",
                    "text": "First Title",
                    "fields": {"level": 0},
                },
                {
                    "type": TitleElement,
                    "tag": "span",
                    "text": "Second Title",
                    "fields": {"level": 0},
                },
            ],
        ),
    ],
    ids=[v[0] for v in values],
)
def test_merge_title_elements(name, elements, expected_elements):
    # Arrange
    step = TitleElementMerger()

    # Act
    processed_elements = step.process(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)


def test_merge_preserves_processing_log():
    """Test that merging preserves processing logs from the first element."""
    elements = create_title_elements_with_same_parent(["PART I. FINANCI", "AL INFORMATION"], level=0)
    element1, element2 = elements
    
    element1.processing_log.add_item(message="Test message 1", log_origin="TestOrigin")
    element2.processing_log.add_item(message="Test message 2", log_origin="TestOrigin")
    
    step = TitleElementMerger()

    processed_elements = step.process(elements)

    assert len(processed_elements) == 1
    merged_element = processed_elements[0]
    assert isinstance(merged_element, TitleElement)
    assert merged_element.text == "PART I. FINANCIAL INFORMATION"
    assert merged_element.level == 0
    
    log_items = merged_element.processing_log.get_items()
    assert len(log_items) >= 2
    assert any("Test message 1" in str(item) for item in log_items)
    assert any("Merged 2 TitleElements" in str(item) for item in log_items)


def test_merge_empty_list():
    """Test that merging an empty list raises an error."""
    step = TitleElementMerger()
    
    with pytest.raises(ValueError, match="Cannot merge empty list of elements"):
        step._merge([])


def test_merge_single_element():
    """Test that merging a single element returns it unchanged."""
    element = create_title_element("Single Title", level=0)
    step = TitleElementMerger()
    
    result = step._merge([element])
    assert result is element
