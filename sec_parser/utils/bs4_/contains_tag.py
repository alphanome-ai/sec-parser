import bs4


def contains_tag(tag: bs4.Tag, name: str, *, include_self: bool = False) -> bool:
    """
    `contains_tag` method checks if the current HTML tag contains a descendant tag
    with the specified name. For example, calling contains_tag("b") on an
    HtmlTag instance representing "<div><p><b>text</b></p></div>" would
    return True, as there is a 'b' tag within the descendants of the 'div' tag.
    """
    if include_self and tag.name == name:
        return True

    return tag.find(name=name) is not None
