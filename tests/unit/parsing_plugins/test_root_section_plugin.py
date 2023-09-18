import pytest
from sec_parser.semantic_elements.semantic_elements import RootSectionSeparatorElement
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
                {"type": RootSectionSeparatorElement, "tag": "document-root-section"},
                {"type": RootSectionElement, "tag": "b"},
                {"type": DummyElement, "tag": "p"},
                {
                    "type": RootSectionElement,
                    "tag": "div",
                    "children": [
                        {"type": RootSectionSeparatorElement, "tag": "document-root-section"},
                        {"type": DummyElement, "tag": "i"},
                    ],
                },
                {"type": DummyElement, "tag": "span"},
            ],
        )
    ],
)
def test_root_section_plugin(html_str, expected_elements):
    # Arrange
    elements = get_elements_from_html(html_str)
    plugin = RootSectionPlugin()

    # Act
    processed_elements = plugin.transform(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
