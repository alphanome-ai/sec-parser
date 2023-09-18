import bs4
from bs4 import NavigableString


def is_unary_tree(tag: bs4.Tag) -> bool:
    """
    `is_unary_tree` determines if a BeautifulSoup tag forms a unary tree.
    In a unary tree, each node has at most one child.

    Unary trees can contain NavigableString leaves. However, if a non-leaf node
    contains a non-empty NavigableString, the tree is not considered unary.

    Additionally, if the some tag is a 'table', the function will return True
    regardless of its children. This is because in the context of this application,
    'table' tags are always considered unary.
    """
    if isinstance(tag, bs4.Tag) and tag.name == "table":
        return True

    children = tuple(
        t
        for t in tag.children
        if not (isinstance(t, NavigableString) and t.strip() == "")
    )

    if len(children) == 0:
        return True

    if len(children) > 1:
        return False

    child = children[0]

    if not isinstance(child, bs4.Tag):
        return True
    return is_unary_tree(child)



