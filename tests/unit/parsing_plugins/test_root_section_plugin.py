import pytest
from sec_parser.semantic_elements.semantic_elements import (
    RootSectionElement,
    UnclaimedElement,
)
from tests.unit.parsing_plugins._utils import get_elements_from_html
from sec_parser.parsing_plugins.root_section_plugin import RootSectionPlugin


@pytest.mark.parametrize(
    "html_str, expected_types, expected_tags",
    [
        (
            """
               <document-root-section></document-root-section>
               <b>0</b>
               <p>1</p>
               <div>
                   <document-root-section></document-root-section>
                   <i>2</i>
               </div>
               <span>3</span>
            """,
            [
                RootSectionElement,
                UnclaimedElement,
                RootSectionElement,
                UnclaimedElement,
            ],
            ["b", "p", "div", "span"],
        )
    ],
)
def test_root_section_plugin(html_str, expected_types, expected_tags):
    # Arrange
    elements = get_elements_from_html(html_str)
    plugin = RootSectionPlugin()

    # Act
    processed_elements = plugin.apply(elements)
    second_run = plugin.apply(processed_elements)

    # Assert
    assert second_run is None  # Plugin should only run once

    assert len(processed_elements) == len(expected_types)
    for ele, expected_type, expected_tag in zip(
        processed_elements, expected_types, expected_tags
    ):
        assert isinstance(ele, expected_type)
        assert ele.html_tag.bs4.name == expected_tag
