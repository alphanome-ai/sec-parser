import pytest

from sec_parser.processing_steps.image_parsing_step import ImageParsingStep
from sec_parser.semantic_elements.semantic_elements import ImageElement
from tests.unit._utils import assert_elements
from tests.unit.processing_steps._utils import parse_initial_semantic_elements


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
    test_image_parsing_step test checks that the ImageParsingStep can successfully
    transform a list of semantic elements returned by `parse_initial_semantic_elements`.
    """
    # Arrange
    elements = parse_initial_semantic_elements(html_str)
    step = ImageParsingStep()

    # Act
    processed_elements = step.process(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
