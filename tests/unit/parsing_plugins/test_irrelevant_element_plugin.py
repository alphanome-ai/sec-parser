import pytest
from sec_parser.parsing_plugins.irrelevant_element_plugin import IrrelevantElementPlugin
from sec_parser.semantic_elements.semantic_elements import IrrelevantElement
from tests.unit.parsing_plugins._utils import (
    get_elements_from_html,
    DummyElement,
    assert_elements,
)
from sec_parser.parsing_plugins import RootSectionPlugin
from sec_parser import (
    RootSectionElement,
)


@pytest.mark.parametrize(
    "html_str, expected_elements",
    [
        (
            """
               <b>0</b>
               <b></b>
            """,
            [
                {"type": DummyElement, "tag": "b"},
                {"type": IrrelevantElement, "tag": "b"},
            ],
        )
    ],
)
def test_root_section_plugin(html_str, expected_elements):
    # Arrange
    elements = get_elements_from_html(html_str)
    plugin = IrrelevantElementPlugin()

    # Act
    processed_elements = plugin.transform(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
