import pytest

from sec_parser.exceptions import SecParserValueError
from sec_parser.utils.py_utils import get_direct_subclass_of_base_class


class Parent:
    pass


class Child(Parent):
    pass


class Grandchild(Child):
    pass


@pytest.mark.parametrize(
    "base, cls, expected",
    [
        (Parent, Child, Child),
        (Parent, Grandchild, Child),
    ],
)
def test_get_direct(base, cls, expected):
    # Arrange
    pass

    # Act
    actual = get_direct_subclass_of_base_class(cls, base)

    # Assert
    assert actual == expected


def test_invalid_input_type():
    # Arrange
    class Unrelated:
        pass

    # Act & Assert
    with pytest.raises(TypeError):
        get_direct_subclass_of_base_class(Unrelated, Parent)


def test_no_direct_subclass():
    with pytest.raises(
        SecParserValueError,
        match=r"Could not find a root child class for the given class below Parent.",
    ):
        get_direct_subclass_of_base_class(Parent, Parent)
