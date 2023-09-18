from __future__ import annotations

import warnings

import bs4

from sec_parser.exceptions.core_exceptions import SecParserValueError
from sec_parser.utils.bs4_.contains_tag import contains_tag
from sec_parser.utils.bs4_.is_unary_tree import is_unary_tree


class HtmlTag:
    """
    HtmlTag class serves as a wrapper around native BeautifulSoup4 Tag objects. The
    primary motivation for introducing this wrapper is to decouple our application
    logic from the underlying library. This abstraction makes it easier to make
    modifications or even switch to a different HTML parsing library in the future
    without requiring extensive changes throughout the codebase.

    The HtmlTag class can also serve as a location to add any extension methods or
    additional properties that are not provided by the native BeautifulSoup4 Tag class,
    thereby further enhancing maintainability and extensibility.
    """

    def __init__(
        self,
        bs4_element: bs4.PageElement,
    ) -> None:
        self._bs4: bs4.Tag = self._to_tag(bs4_element)

        # Cached properties
        self._text: str | None = None
        self._children: list[HtmlTag] | None = None
        self._is_unary_tree: bool | None = None

    def get_text(self) -> str:
        """
        `text` is a cached property. The text is extracted recursively
        from the children elements. This operation can be computationally
        expensive, hence the result is cached as the underlying data
        doesn't change.
        """
        self._text = self._bs4.get_text().strip() if self._text is None else self._text
        return self._text

    @property
    def name(self) -> str:
        return self._bs4.name

    def get_children(self) -> list[HtmlTag]:
        self._children = (
            [
                HtmlTag(self._to_tag(child))
                for child in self._bs4.children
                if not (isinstance(child, bs4.NavigableString) and child.strip() == "")
            ]
            if self._children is None
            else self._children
        )
        return self._children

    def contains_tag(self, name: str, *, include_self: bool = False) -> bool:
        """
        `contains_tag` method checks if the current HTML tag contains a descendant tag
        with the specified name. For example, calling contains_tag("b") on an
        HtmlTag instance representing "<div><p><b>text</b></p></div>" would
        return True, as there is a 'b' tag within the descendants of the 'div' tag.
        """
        return contains_tag(self._bs4, name, include_self=include_self)

    def is_unary_tree(self) -> bool:
        """
        `is_unary_tree` determines if a BeautifulSoup tag forms a unary tree.
        In a unary tree, each node has at most one child.

        However, if a non-leaf node contains a non-empty string even without a tag
        surrounding it, the tree is not considered unary.

        Additionally, if the some tag is a 'table', the function will return True
        regardless of its children. This is because in the context of this application,
        'table' tags are always considered unary.
        """
        self._is_unary_tree = (
            is_unary_tree(self._bs4)
            if self._is_unary_tree is None
            else self._is_unary_tree
        )
        return self._is_unary_tree

    @staticmethod
    def _to_tag(element: bs4.PageElement) -> bs4.Tag:
        if isinstance(element, bs4.Tag):
            tag = element
        elif isinstance(element, bs4.NavigableString):
            if str(element).strip() == "":
                msg = "NavigableString is empty"
                raise EmptyNavigableStringError(msg)
            tag = bs4.Tag(name="span")
            tag.string = str(element)
            msg = "Converting bs4.NavigableString to bs4.Tag(<span>)"
            warnings.warn(msg, stacklevel=2)
        else:
            msg = f"Unsupported element type: {type(element).__name__}"
            raise TypeError(msg)
        return tag


class EmptyNavigableStringError(SecParserValueError):
    pass
