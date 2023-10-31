from __future__ import annotations

from typing import TYPE_CHECKING

import bs4
import xxhash
from frozendict import frozendict
from loguru import logger

from sec_parser.exceptions import SecParserValueError
from sec_parser.utils.bs4_.approx_table_metrics import (
    ApproxTableMetrics,
    get_approx_table_metrics,
)
from sec_parser.utils.bs4_.contains_tag import contains_tag
from sec_parser.utils.bs4_.count_tags import count_tags
from sec_parser.utils.bs4_.has_tag_children import has_tag_children
from sec_parser.utils.bs4_.has_text_outside_tags import has_text_outside_tags
from sec_parser.utils.bs4_.is_unary_tree import is_unary_tree
from sec_parser.utils.bs4_.text_styles_metrics import compute_text_styles_metrics
from sec_parser.utils.bs4_.without_tags import without_tags
from sec_parser.utils.bs4_.wrap_tags_in_new_parent import wrap_tags_in_new_parent

if TYPE_CHECKING: # pragma: no cover
    from collections.abc import Iterable

TEXT_PREVIEW_LENGTH = 40


class HtmlTag:
    """
    The HtmlTag class is a wrapper for BeautifulSoup4 Tag objects.

    It serves three main purposes:

    1. Decoupling: By abstracting the underlying BeautifulSoup4 library, we
       can isolate our application logic from the library specifics. This
       makes it easier to modify or even replace the HTML parsing library in
       the future without extensive codebase changes.

    2. Usability: The HtmlTag class provides a convenient location to add
       extension methods or additional properties not offered by the native
       BeautifulSoup4 Tag class. This enhances the usability of the class.

    3. Caching: The HtmlTag class also caches processing results, improving
       performance by avoiding unnecessary re-computation.
    """

    def __init__(
        self,
        bs4_element: bs4.PageElement,
    ) -> None:
        self._bs4: bs4.Tag = self._to_tag(bs4_element)

        # We use cached properties to prevent performance issues in intensive loops.
        # As the source code is immutable, we can afford to use some extra memory
        # for caching. A decorator might be a cleaner solution here.
        self._text: str | None = None
        self._children: list[HtmlTag] | None = None
        self._is_unary_tree: bool | None = None
        self._first_deepest_tag: HtmlTag | None | NotSetType = NotSet
        self._text_styles_metrics: dict[tuple[str, str], float] | None = None
        self._frozen_dict: frozendict | None = None
        self._source_code: str | None = None
        self._pretty_source_code: str | None = None
        self._approx_table_metrics: ApproxTableMetrics | None = None
        self._contains_tag: dict[tuple[str, bool], bool] = {}
        self._without_tags: dict[tuple[str, ...], HtmlTag] = {}
        self._count_tags: dict[str, int] = {}
        self._has_text_outside_tags: dict[tuple[str, ...], bool] = {}
        self._contains_words: bool | None = None

    def get_source_code(self, *, pretty: bool = False) -> str:
        if pretty:
            if self._pretty_source_code is None:
                self._pretty_source_code = self._bs4.prettify()
            return self._pretty_source_code

        if self._source_code is None:
            self._source_code = str(self._bs4)
        return self._source_code

    def _generate_preview(self, text: str) -> str:
        """Generate a preview of the text with a specified length."""
        text = text.replace("\n", " ").strip()
        return (
            text[: TEXT_PREVIEW_LENGTH // 2]
            + f"...[{len(text) - TEXT_PREVIEW_LENGTH}]..."
            + text[-TEXT_PREVIEW_LENGTH // 2 :]
            if len(text) > TEXT_PREVIEW_LENGTH
            else text
        )

    def to_dict(self) -> frozendict:
        """Compute the hash of the HTML tag."""
        if self._frozen_dict is None:
            self._frozen_dict = frozendict(
                {
                    "tag_name": self._bs4.name,
                    "text_preview": self._generate_preview(self.text),
                    "html_preview": self._generate_preview(self.get_source_code()),
                    "html_hash": xxhash.xxh32(self.get_source_code()).hexdigest(),
                },
            )
        return self._frozen_dict

    def contains_words(self) -> bool:
        """Return True if the semantic element contains text."""
        if self._contains_words is None:
            self._contains_words = (
                any(char.isalpha() for char in self.text) if self.text else False
            )
        return self._contains_words

    @property
    def text(self) -> str:
        """
        `text` property recursively extracts text from the child tags.
        The result is cached as the underlying data doesn't change.
        """
        if self._text is None:
            self._text = self._bs4.text.strip()
        return self._text

    @property
    def name(self) -> str:
        """Returns tag name, e.g. for <div> return 'div'."""
        return self._bs4.name.lower()

    def has_tag_children(self) -> bool:
        return has_tag_children(self._bs4)

    def get_children(self) -> list[HtmlTag]:
        if self._children is None:
            self._children = [
                HtmlTag(child)
                for child in self._bs4.children
                if not (isinstance(child, bs4.NavigableString) and child.strip() == "")
            ]
        return self._children

    def contains_tag(self, name: str, *, include_self: bool = False) -> bool:
        """
        `contains_tag` method checks if the current HTML tag contains a descendant tag
        with the specified name. For example, calling contains_tag("b") on an
        HtmlTag instance representing "<div><p><b>text</b></p></div>" would
        return True, as there is a 'b' tag within the descendants of the 'div' tag.
        """
        tag_key = (name, include_self)
        if self._contains_tag.get(tag_key) is None:
            self._contains_tag[tag_key] = contains_tag(
                self._bs4,
                name,
                include_self=include_self,
            )
        return self._contains_tag[tag_key]

    def has_text_outside_tags(self, tags: list[str] | str) -> bool:
        """
        `has_text_outside_tags` function checks if the given
        node has any text outside the specified tag.
        For example, calling has_text_outside_tags(node, ["b"])
        on a node representing "<div><p><b>text</b>extra text</p></div>"
        would return True, as there is text outside the 'b'
        tag within the descendants of the 'div' tag.
        """
        tag_names = tuple(tags if isinstance(tags, list) else [tags])
        if tag_names not in self._has_text_outside_tags:
            self._has_text_outside_tags[tag_names] = has_text_outside_tags(
                self._bs4,
                tag_names,
            )
        return self._has_text_outside_tags[tag_names]

    def without_tags(self, names: Iterable[str]) -> HtmlTag:
        """
        `without_tags` method creates a copy of the current HTML tag and removes all
        descendant tags with the specified name. For example, calling
        without_tags(tag, ["b","i"]) on an HtmlTag instance representing
        "<div><b>foo</b><p>bar<i>bax</i></p></div>" would
        return a copy HtmlTag instance representing "<div><p>bar</p></div>".
        """
        tag_key = tuple(names)
        if self._without_tags.get(tag_key) is None:
            self._without_tags[tag_key] = HtmlTag(
                without_tags(
                    self._bs4,
                    names,
                ),
            )
        return self._without_tags[tag_key]

    def count_tags(self, name: str) -> int:
        """
        `count_tags` method counts the number of descendant tags with the specified name
        within the current HTML tag. For example, calling count_tags("b") on an
        HtmlTag instance representing "<div><p><b>text</b></p><b>more text</b></div>"
        would return 2, as there are two 'b' tags within the descendants of
        the 'div' tag.
        """
        tag_key = name
        if self._count_tags.get(tag_key) is None:
            self._count_tags[tag_key] = count_tags(
                self._bs4,
                name,
            )
        return self._count_tags[tag_key]

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
        if self._is_unary_tree is None:
            self._is_unary_tree = is_unary_tree(self._bs4)
        return self._is_unary_tree

    def get_text_styles_metrics(self) -> dict[tuple[str, str], float]:
        """
        Compute the percentage distribution of various CSS styles within the text
        content of a given HTML tag and its descendants.

        This function iterates through all the text nodes within the tag, recursively
        includes text from child elements, and calculates the effective styles applied
        to each text segment.

        It aggregates these styles and computes their percentage distribution based
        on the length of text they apply to.

        The function uses BeautifulSoup's recursive text search and parent traversal
        features. It returns a dictionary containing the aggregated style metrics
        (the percentage distribution of styles).

        Each dictionary entry corresponds to a unique style, (property, value) and
        the percentage of text it affects.
        """
        if self._text_styles_metrics is None:
            self._text_styles_metrics = compute_text_styles_metrics(self._bs4)
        return self._text_styles_metrics

    def get_approx_table_metrics(self) -> ApproxTableMetrics:
        if self._approx_table_metrics is None:
            self._approx_table_metrics = get_approx_table_metrics(self._bs4)
        return self._approx_table_metrics

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
            logger.trace("Converting bs4.NavigableString to bs4.Tag(<span>)")
        else:
            msg = f"Unsupported element type: {type(element).__name__}"
            raise TypeError(msg)
        return tag

    @staticmethod
    def wrap_tags_in_new_parent(
        parent_tag_name: str,
        tags: Iterable[HtmlTag],
    ) -> HtmlTag:
        return HtmlTag(
            wrap_tags_in_new_parent(
                parent_tag_name,
                [tag._bs4 for tag in tags],  # noqa: SLF001
            ),
        )


class EmptyNavigableStringError(SecParserValueError):
    pass


class NotSetType:
    pass


NotSet = NotSetType()
NotSet = NotSetType()
NotSet = NotSetType()
