import pytest

from sec_parser import RootSectionElement
from sec_parser.processing_steps import RootSectionParsingStep
from sec_parser.semantic_elements.semantic_elements import (
    RootSectionSeparatorElement,
    UndeterminedElement,
)
from tests.unit.processing_steps._utils import assert_elements, get_elements_from_html


@pytest.mark.parametrize(
    ("html_str", "expected_elements"),
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
        ),
    ],
)
def test_root_section_step(html_str, expected_elements):
    """
    This test checks that the RootSectionParsingStep can successfully transform a list of
    semantic elements returned by `get_elements_from_html`. These elements can be
    of type `UndeterminedElement` or `SpecialElement`.
    """
    # Arrange
    elements = get_elements_from_html(html_str)
    step = RootSectionParsingStep()

    # Act
    processed_elements = step.process(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
