from sec_parser.semantic_tree_transformations.tree_node import TreeNode


class SemanticTree:
    def __init__(self, root_nodes: list[TreeNode]) -> None:
        self.root_nodes = root_nodes
