import bs4
from bs4 import NavigableString


def has_text_outside_tags(node: bs4.PageElement, tag_names: tuple[str, ...]) -> bool:
    """
    `has_text_outside_tag` function checks if the given
    node has any text outside the specified tag.
    For example, calling has_text_outside_tag(node, "b")
    on a node representing "<div><p><b>text</b>extra text</p></div>"
    would return True, as there is text outside the 'b'
    tag within the descendants of the 'div' tag.
    """
    if isinstance(node, NavigableString) and any(not c.isspace() for c in node):
        return True
    if isinstance(node, bs4.Tag):
        if node.name in tag_names:
            return False
        for child in node.children:
            if has_text_outside_tags(child, tag_names):
                return True
    return False
