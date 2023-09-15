import pytest
from sec_parser import (
    RootSectionElement,
    UndeterminedElement,
)
from tests.unit.parsing_plugins._utils import get_elements_from_html
from sec_parser.parsing_plugins import RootSectionPlugin


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
                UndeterminedElement,
                RootSectionElement,
                UndeterminedElement,
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
    processed_elements = plugin.transform(elements)

    # Assert
    assert len(processed_elements) == len(expected_types)
    for ele, expected_type, expected_tag in zip(
        processed_elements, expected_types, expected_tags
    ):
        assert isinstance(ele, expected_type)
        assert ele.html_tag.bs4.name == expected_tag
