"""
The utils subpackage contains utility functions
and helpers used across the sec_parser project.
"""


from sec_parser.utils.bs4_.is_unary_tree import is_unary_tree
from sec_parser.utils.env_var_helpers import ValueNotSetError, get_value_or_env_var

__all__ = [
    "ValueNotSetError",
    "get_value_or_env_var",
    "is_unary_tree",
]
