from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterator

    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )
    from sec_parser.semantic_tree.tree_node import TreeNode


class SemanticTree:
    def __init__(self, root_nodes: list[TreeNode]) -> None:
        self._root_nodes = root_nodes

    def __iter__(self) -> Iterator[TreeNode]:
        """Iterate over the root nodes of the tree."""
        yield from self._root_nodes

    @property
    def nodes(self) -> Iterator[TreeNode]:
        """
        Get all nodes in the semantic tree. This includes the root nodes and all
        their descendants.
        """
        for node in self._root_nodes:
            yield node
            yield from node.get_descendants()

    def render(
        self,
        *,
        pretty: bool | None = True,
        ignored_types: tuple[type[AbstractSemanticElement], ...] | None = None,
        char_display_limit: int | None = None,
        verbose: bool = False,
    ) -> str:
        """
        Render the semantic tree as a human-readable string.

        Syntactic sugar for a more convenient usage of `render`.
        """
        from sec_parser.semantic_tree.render_ import render

        return render(
            self,
            pretty=pretty,
            ignored_types=ignored_types,
            char_display_limit=char_display_limit,
            verbose=verbose,
        )

    def print(  # noqa: A003
        self,
        *,
        pretty: bool | None = True,
        ignored_types: tuple[type[AbstractSemanticElement], ...] | None = None,
        char_display_limit: int | None = None,
        verbose: bool = False,
        line_limit: int | None = None,
    ) -> None:
        """
        Print the semantic tree as a human-readable string.

        Syntactic sugar for a more convenient usage of `render`.
        """
        rendered = self.render(
            pretty=pretty,
            ignored_types=ignored_types,
            char_display_limit=char_display_limit,
            verbose=verbose,
        )
        if line_limit is not None:
            rendered = "\n".join(rendered.split("\n")[:line_limit])
        print(rendered)  # noqa: T201
