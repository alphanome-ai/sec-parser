from __future__ import annotations

from typing import cast

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import IrrelevantElement
from sec_parser.semantic_tree.semantic_tree import SemanticTree
from sec_parser.semantic_tree.tree_node import TreeNode

DEFAULT_CHAR_DISPLAY_LIMIT = 65


def render(  # noqa: C901, PLR0912
    tree: list[TreeNode] | TreeNode | SemanticTree | list[AbstractSemanticElement],
    *,
    pretty: bool | None = True,
    ignored_types: tuple[type[AbstractSemanticElement], ...] | None = None,
    char_display_limit: int | None = None,
    verbose: bool = False,
    _nodes: list[TreeNode] | None = None,
    _level: int = 0,
    _prefix: str = "",
    _is_root: bool = True,
) -> str:
    """
    render function is used to visualize the structure of the semantic tree.
    It is primarily used for debugging purposes.
    """
    if isinstance(tree, TreeNode):
        root_nodes = [tree]
    elif isinstance(tree, SemanticTree):
        root_nodes = list(tree)
    elif isinstance(tree, list) and tree:
        if all(isinstance(e, AbstractSemanticElement) for e in tree):
            elements = cast(list[AbstractSemanticElement], tree)
            root_nodes = [TreeNode(e) for e in elements]
        elif all(isinstance(e, TreeNode) for e in tree):
            root_nodes = cast(list[TreeNode], tree)
        else:
            msg = "All elements in the tree must be of type AbstractSemanticElement or TreeNode"
            raise TypeError(msg)
    else:
        msg = "Invalid type for 'tree'. Expected TreeNode, SemanticTree, list[AbstractSemanticElement], or list[TreeNode]"
        raise TypeError(msg)
    pretty = pretty if pretty is not None else True
    ignored_types = ignored_types or (IrrelevantElement,)
    char_display_limit = (
        char_display_limit
        if char_display_limit and char_display_limit > 0
        else DEFAULT_CHAR_DISPLAY_LIMIT
    )

    tree_strings = []
    _nodes = _nodes if _nodes is not None else root_nodes

    for i, node in enumerate(_nodes):
        element = node.semantic_element
        if isinstance(element, ignored_types):
            continue

        is_last = i == len(_nodes) - 1

        indent = "├── " if not is_last else "└── "
        new_prefix = "│   " if not is_last else "    "

        level = ""
        lvl = getattr(node.semantic_element, "level", None)
        if verbose and lvl is not None:
            level = f"[L{lvl}]"
            if pretty:
                level = f"\033[1;92m{level}\033[0m"
        class_name = f"{element.__class__.__name__}{level}"
        contents = element.get_summary().strip()
        if len(contents) > char_display_limit:
            half_limit = (char_display_limit - 3) // 2  # Subtract 3 for the "..."
            contents = f"{contents[:half_limit]}...{contents[-half_limit:]}"
        if pretty:
            class_name = f"\033[1;34m{class_name}\033[0m"

        # Fix the alignment for root elements
        line = f"{_prefix}{indent}{class_name}" if not _is_root else f"{class_name}"
        if contents:
            line = f"{line}: {contents}"
        tree_strings.append(line)

        # Recursive call: Always set _is_root to False for non-root elements
        tree_strings.append(
            render(
                root_nodes,
                pretty=pretty,
                ignored_types=ignored_types,
                char_display_limit=char_display_limit,
                verbose=verbose,
                _nodes=node.children,
                _level=_level + 1,
                _prefix=_prefix + (_prefix if _is_root else new_prefix),
                _is_root=False,
            ),
        )

    return "\n".join(filter(None, tree_strings))
