import bs4

from sec_parser.exceptions import SecParserValueError


class NoTableFoundError(SecParserValueError):
    pass


class MultipleTablesFoundError(SecParserValueError):
    pass


def get_single_table(bs4_tag: bs4.Tag) -> bs4.Tag:
    if bs4_tag.name == "table":
        return bs4_tag
    tables = bs4_tag.find_all("table")
    if not tables:
        msg = "No <table> tag found in the provided html."
        raise NoTableFoundError(msg)
    if len(tables) > 1:
        msg = "Multiple <table> tags found in the provided html."
        raise MultipleTablesFoundError(msg)
    table = tables[0]
    if not isinstance(table, bs4.Tag):  # pragma: no cover
        msg = f"Expected a bs4.Tag, got {type(table)} instead."
        raise TypeError(msg)
    return table
