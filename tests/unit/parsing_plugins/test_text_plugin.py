import pytest

from sec_parser import TextElement
from sec_parser.parsing_plugins import TextPlugin
from sec_parser.semantic_elements.semantic_elements import (IrrelevantElement,
                                                            TextElement)
from tests.unit.parsing_plugins._utils import (SpecialElement, assert_elements,
                                               get_elements_from_html)


@pytest.mark.parametrize(
    "html_str, expected_elements",
    [
        (
            """
               <special></special>
               <p>1</p>
               <div>
                   <i>2</i>
                   <p></p>
               </div>
               <span>3</span>
            """,
            [
                {"type": SpecialElement, "tag": "special"},
                {"type": TextElement, "tag": "p"},
                {
                    "type": TextElement,
                    "tag": "div",
                    "children": [
                        {"type": TextElement, "tag": "i"},
                        {"type": IrrelevantElement, "tag": "p"},
                    ],
                },
                {"type": TextElement, "tag": "span"},
            ],
        ),
    ],
)
def test_text_plugin(html_str, expected_elements):
    """
    This test checks that the TextPlugin can successfully transform a list of 
    semantic elements returned by `get_elements_from_html`. These elements can be 
    of type `UndeterminedElement` or `SpecialElement`.
    """

    # Arrange
    elements = get_elements_from_html(html_str)
    plugin = TextPlugin(except_dont_process={SpecialElement})

    # Act
    processed_elements = plugin.transform(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
