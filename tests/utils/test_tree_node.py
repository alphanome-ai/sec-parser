from sec_parser._utils import TreeNode


def test_create_node():
    node = TreeNode()
    assert node.parent is None
    assert node.children == []


def test_add_remove_child():
    parent = TreeNode()
    child = TreeNode()
    parent.add_child(child)
    assert child in parent.children
    assert child.parent == parent

    parent.remove_child(child)
    assert child not in parent.children
    assert child.parent is None


def test_add_children():
    parent = TreeNode()
    children = [TreeNode(), TreeNode(), TreeNode()]
    parent.add_children(children)
    assert all(child in parent.children for child in children)
    assert all(child.parent == parent for child in children)


def test_has_child():
    parent = TreeNode()
    child = TreeNode()
    parent.add_child(child)
    assert parent.has_child(child)


def test_parent_setter():
    parent1 = TreeNode()
    parent2 = TreeNode()
    child = TreeNode(parent=parent1)
    assert child.parent == parent1
    assert child in parent1.children

    child.parent = parent2
    assert child.parent == parent2
    assert child not in parent1.children
    assert child in parent2.children


def test_repr():
    parent = TreeNode()
    children = [TreeNode(parent=parent), TreeNode(parent=parent)]
    assert repr(parent) == f"TreeNode(parent=None, children={len(children)})"


def test_create_node_with_children():
    children = [TreeNode(), TreeNode(), TreeNode()]
    parent = TreeNode(children=children)
    assert parent.parent is None
    assert all(child in parent.children for child in children)
    assert all(child.parent == parent for child in children)
