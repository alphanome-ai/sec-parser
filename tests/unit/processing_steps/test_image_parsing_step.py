import pytest

from sec_parser.processing_steps.image_parsing_step import ImageParsingStep
from sec_parser.semantic_elements.semantic_elements import ImageElement
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
                <div>
                <div>
                <img src="image.jpg" alt="Description of image" width="500" height="600">
                </div>
                </div>
            """,
            [
                {"type": ImageElement, "tag": "div"},
            ],
        ),
    ],
)
def test_image_parsing_step(html_str, expected_elements):
    """
    test_image_parsing_step test checks that the ImageParsingStep can successfully transform a list of
    semantic elements returned by `get_elements_from_html`. These elements can be
    of type `UndeterminedElement` or `SpecialElement`.
    """
    # Arrange
    elements = get_elements_from_html(html_str)
    step = ImageParsingStep(types_to_exclude={SpecialElement})

    # Act
    processed_elements = step.process(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
    assert_elements(processed_elements, expected_elements)
