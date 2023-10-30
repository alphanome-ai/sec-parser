from collections.abc import Iterable

import bs4


def wrap_tags_in_new_parent(parent_tag_name: str, tags: Iterable[bs4.Tag]) -> bs4.Tag:
    soup = bs4.BeautifulSoup("", "html.parser")
    new_tag = soup.new_tag(parent_tag_name)
    for tag in tags:
        new_tag.append(tag)
    return new_tag
