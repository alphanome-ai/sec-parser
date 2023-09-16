from sec_parser import (
    AbstractNestingRule,
    BaseSemanticElement,
    HtmlTag,
    TreeBuilder,
)


class ParentElement(BaseSemanticElement):
    pass


class ChildElement(BaseSemanticElement):
    pass


class ParentChildNestingRule(AbstractNestingRule):
    def should_be_nested_under(
        self,
        parent: BaseSemanticElement,
        child: BaseSemanticElement,
    ) -> bool:
        return isinstance(parent, ParentElement) and isinstance(child, ChildElement)


def test_build():
    # Arrange
    mock_elements = [
        ParentElement(None),
        ChildElement(None),
    ]
    tree_builder = TreeBuilder(create_default_rules=lambda: [ParentChildNestingRule()])

    # Act
    tree = tree_builder.build(mock_elements)

    # Assert
    assert len(tree.root_nodes) == 1
    assert isinstance(tree.root_nodes[0].semantic_element, ParentElement)
    assert len(tree.root_nodes[0].children) == 1
    assert isinstance(tree.root_nodes[0].children[0].semantic_element, ChildElement)
