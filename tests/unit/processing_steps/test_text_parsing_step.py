import pytest

from sec_parser import TextElement
from sec_parser.processing_steps import TextParsingStep
from sec_parser.semantic_elements.semantic_elements import (
    IrrelevantElement,
    TextElement,
)
from tests.unit.processing_steps._utils import (
    SpecialElement,
    assert_elements,
    get_elements_from_html,
)


@pytest.mark.parametrize(
    ("html_str", "expected_elements"),
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
def test_text_step(html_str, expected_elements):
    """
    This test checks that the TextParsingStep can successfully transform a list of
    semantic elements returned by `get_elements_from_html`. These elements can be
    of type `UndeterminedElement` or `SpecialElement`.
    """
    # Arrange
    elements = get_elements_from_html(html_str)
    step = TextParsingStep(except_dont_process={SpecialElement})

    # Act
    processed_elements = step.process(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
