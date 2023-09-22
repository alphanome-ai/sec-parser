import pytest

from sec_parser import RootSectionElement
from sec_parser.parsing_plugins import RootSectionPlugin
from sec_parser.semantic_elements.semantic_elements import (
    RootSectionSeparatorElement, UndeterminedElement)
from tests.unit.parsing_plugins._utils import (assert_elements,
                                               get_elements_from_html)


@pytest.mark.parametrize(
    "html_str, expected_elements",
    [
        (
            """<document-root-section></document-root-section>
               <b>0</b>
               <p>1</p>
               <div>
                   <document-root-section></document-root-section>
                   <i>2</i>
               </div>
               <span>3</span>""",
            [
                {"type": RootSectionSeparatorElement, "tag": "document-root-section"},
                {"type": RootSectionElement, "tag": "b"},
                {"type": UndeterminedElement, "tag": "p"},
                {
                    "type": RootSectionElement,
                    "tag": "div",
                    "children": [
                        {
                            "type": RootSectionSeparatorElement,
                            "tag": "document-root-section",
                        },
                        {"type": UndeterminedElement, "tag": "i"},
                    ],
                },
                {"type": UndeterminedElement, "tag": "span"},
            ],
        )
    ],
)
def test_root_section_plugin(html_str, expected_elements):
    """
    This test checks that the RootSectionPlugin can successfully transform a list of 
    semantic elements returned by `get_elements_from_html`. These elements can be 
    of type `UndeterminedElement` or `SpecialElement`.
    """

    # Arrange
    elements = get_elements_from_html(html_str)
    plugin = RootSectionPlugin()

    # Act
    processed_elements = plugin.transform(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
