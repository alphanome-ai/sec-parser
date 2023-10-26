import bs4


def count_tags(tag: bs4.Tag, name: str) -> int:
    """
    `count_tags` method counts the number of descendant tags with the specified name
    within the current HTML tag. For example, calling count_tags("b") on an
    HtmlTag instance representing "<div><p><b>text</b></p><b>more text</b></div>"
    would return 2, as there are two 'b' tags within the descendants of the 'div' tag.
    """
    count = 0
    if tag.name == name:
        count += 1
    count += len(tag.find_all(name=name))
    return count
