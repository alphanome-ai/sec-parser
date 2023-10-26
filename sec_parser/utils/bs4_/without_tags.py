import copy
from collections.abc import Iterable

import bs4


def without_tags(tag: bs4.Tag, names: Iterable[str]) -> bs4.Tag:
    """
    `without_tags` method creates a copy of the current HTML tag and removes all
    descendant tags with the specified name. For example, calling
    without_tags(tag, ["b","i"]) on an HtmlTag instance representing
    "<div><b>foo</b><p>bar<i>bax</i></p></div>" would
    return a copy HtmlTag instance representing "<div><p>bar</p></div>".
    """
    tag_copy = copy.deepcopy(tag)
    for name in names:
        for descendant in tag_copy.find_all(name=name):
            descendant.decompose()
    return tag_copy
