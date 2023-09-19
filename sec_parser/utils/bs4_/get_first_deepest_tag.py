from __future__ import annotations

import bs4


def get_first_deepest_tag(tag: bs4.Tag) -> bs4.Tag | None:
    """
    Given a BeautifulSoup tag, returns the first deepest tag within it.

    For example, if we have the following HTML structure:
    <div><p>Test</p><span>Another Test</span></div>
    and we pass the 'div' tag to this function, it will return the 'p' tag,
    which is the first deepest tag within the 'html' tag.
    """
    deepest_tag: bs4.PageElement = tag

    while isinstance(deepest_tag, bs4.Tag):
        # Filter out any NavigableString instances that are just whitespace
        contents = [
            content
            for content in deepest_tag.contents
            if not (isinstance(content, bs4.NavigableString) and content.strip() == "")
        ]

        # Break if there are no tags within the deepest_tag
        if not any(isinstance(content, bs4.Tag) for content in contents):
            break

        deepest_tag = contents[0]

    return deepest_tag if isinstance(deepest_tag, bs4.Tag) else None
