import re

from sec_parser.exceptions import SecParserValueError

MAX_THRESHOLD = 100.0


def get_direct_subclass_of_base_class(cls: type, base_class: type) -> type:
    """
    Given a class, find the class that is one step below
    the specified base_class in its inheritance hierarchy.
    """
    if not issubclass(cls, base_class):
        msg = f"Argument must be a subclass of {base_class.__name__}."
        raise TypeError(msg)

    root_child = None
    for ancestor in cls.mro():
        if ancestor is base_class:
            break
        root_child = ancestor

    if root_child is None:
        msg = (
            f"Could not find a root child class for "
            f"the given class below {base_class.__name__}."
        )
        raise SecParserValueError(msg)

    return root_child


def clean_whitespace(input_str: str) -> str:
    """Replace newlines and any following spaces with a single space."""
    return re.sub(r"\s+", " ", input_str).strip()


def normalize_string(input_str: str) -> str:
    input_str = input_str.lower()
    # Remove all characters that are not a-z, 0-9, or whitespace
    input_str = re.sub(r"[^a-z0-9\s]", "", input_str)
    # Replace multiple whitespaces with a single space
    input_str = re.sub(r"\s+", " ", input_str)
    return clean_whitespace(input_str)


def exceeds_capitalization_threshold(s: str, threshold: float) -> bool:
    """
    Calculate the percentage of capitalized letters in a given string `s`.
    Only counts characters that can be capitalized (alphabetic characters).
    """
    if not 0 <= threshold <= MAX_THRESHOLD:
        msg = "Threshold must be between 0 and 100."
        raise SecParserValueError(msg)
    if not s:
        return False

    current_percentage = 0.0
    total_alpha = 0
    total_capital = 0

    for _idx, char in enumerate(s):
        if char.isalpha():
            total_alpha += 1
            if char.isupper():
                total_capital += 1

    current_percentage = (total_capital / total_alpha) * 100 if total_alpha else 0.0
    return current_percentage >= threshold
