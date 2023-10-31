import bs4


def has_tag_children(bs4_tag: bs4.Tag) -> bool:
    return any(True for _ in bs4_tag.children if isinstance(_, bs4.Tag))
